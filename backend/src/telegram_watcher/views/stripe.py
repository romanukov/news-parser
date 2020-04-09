from rest_framework.views import APIView, Response
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ParseError

from rest_framework_jwt.serializers import JSONWebTokenSerializer

from datetime import datetime

import stripe
import stripe.error

from app.env import env
from ..models import Subscription, User

import django.template.loader as template_loader
from django.core.mail import send_mail
import logging

stripe.api_key = env("STRIPE_SECRET")

__all__ = ("StripeCheckoutView",
          "StripeEventView",
          "RegistrationView",
          "StripeDescriptionView")

STRIPE_PLAN = env("STRIPE_PLAN")

class StripeDescriptionView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        product = stripe.Product.retrieve(env("STRIPE_PRODUCT"))
        plan = stripe.Plan.retrieve(env("STRIPE_PLAN"))
        return Response({
            "name": product.name,
            "description": product.statement_descriptor,
            "amount": plan.amount,
            "public_key": env("STRIPE_PUBLIC"),
        }, headers={
            'Access-Control-Allow-Credentials': True,
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
        })

class StripeCheckoutView(APIView):
    # Checkout from profile
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data
        stripe_customer, stripe_created = \
            user.get_or_create_stripe_customer(data['id'])

        if stripe_created:  # New stripe customer
            stripe_subscription = stripe.Subscription.create(
                customer=stripe_customer.id,
                items=[
                    {
                        "plan": STRIPE_PLAN,
                    },
                ]
            )
            Subscription.objects.create(
                user=user,
                stripe_token=stripe_subscription.id,
                till=datetime.fromtimestamp(
                    stripe_subscription.current_period_end
                )
            )
        else:  # Exists stripe customer
            subscription = user.latest_created_subscribe()  # Try to find sub
            if subscription is None:  # Sub not find
                stripe_subscriptions = user.stripe_get_subscriptions(STRIPE_PLAN)
                stripe_subscription = stripe_subscriptions.get("data")[0]
                Subscription.objects.create(
                    user=user,
                    stripe_token=stripe_subscription.id,
                    till=datetime.fromtimestamp(
                        stripe_subscription.current_period_end
                    )
                )
            else:  # Sub find
                try:
                    stripe_subscription = stripe.Subscription.retrieve(
                        subscription.stripe_token
                    )  # Find old sub in stripe
                    till = datetime.fromtimestamp(
                        stripe_subscription.current_period_end
                    )
                    if till != subscription.till:
                        subscription.till = till
                        subscription.save()
                except stripe.error.InvalidRequestError:
                    pass
        return Response({"success": True})


class StripeEventView(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def invoice_payment_suceeded(invoice):
        try:
            user = User.objects.get(stripe_token=invoice["customer"])
            subscription = user.latest_created_subscribe()
            if (
                subscription is None or
                subscription.stripe_token !=
                invoice["subscription"]
            ):
                Subscription.objects.create(
                    stripe_token=invoice["subscription"],
                    user=user,
                    till=invoice["period_end"]
                )
        except User.DoesNotExist:
            try:
                subscription = Subscription.objects.get(
                    stripe_token=invoice["subscription"]
                )
            except Subscription.DoesNotExist:
                return False
            subscription.till = invoice["period_end"]
            subscription.save()
            user = subscription.user
            user.stripe_token = invoice["customer"]
            user.save()
        return True
    
    def post(self, request):
        # Subscription charge
        print("Stripe webhook recieved, event type:", request.data.get("type"))
        if request.data.get("type") == "invoice.payment_succeeded":
            if not self.invoice_payment_suceeded(request.data["data"]["object"]):
                # logging.error(f"Stripe invoice event hook error: {str(request.data)}")
                pass
        return Response()


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, min_length=6)
    stripe_token = serializers.CharField(required=True)


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def registration_email(self, **context):
        from_email = env("EMAIL_FROM")
        to_email = context.get("email")
        token = context.get("token")

        subject = "Welcome to SamFeeds!"
        mail_string = template_loader.render_to_string(
            "registration_email.html",
            context={
                "email": to_email,
                "login_link": "https://app.samfeeds.com/?access=%s" % token
            }
        )
        return send_mail(subject, "Welcome to SamFeeds!", from_email, [to_email], html_message=mail_string)

    def post(self, request):
        validated = RegistrationSerializer(data=request.data)
        validated.is_valid(True)
        if User.objects.filter(
                username=validated.validated_data["email"]
        ).exists():
            raise ParseError("User with this email is exists")
        try:
            stripe_customer = stripe.Customer.create(
                email=validated.validated_data["email"],
                source=validated.validated_data["stripe_token"]
            )
        except stripe.error.InvalidRequestError:
            raise ParseError("Invalid stripe token")

        user = User(
            email=validated.validated_data["email"],
            username=validated.validated_data["email"],
            is_subscriber=True
        )
        user.set_password(validated.validated_data["password"])
        user.stripe_token = stripe_customer.get('id')
        user.save()
        stripe_subscription = stripe.Subscription.create(
            customer=stripe_customer.id,
            items=[
                {
                    "plan": STRIPE_PLAN,
                },
            ]
        )
        Subscription.objects.create(
            user=user,
            stripe_token=stripe_subscription.id,
            till=datetime.fromtimestamp(
                stripe_subscription.current_period_end
            )
        )
        token = JSONWebTokenSerializer().validate(
            {
                "username": user.username,
                "password": validated.validated_data["password"]
            }
        ).get("token")
        self.registration_email(email=user.email, token=token)
        return Response({"token": token})
