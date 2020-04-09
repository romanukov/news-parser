from rest_framework import serializers

from telegram_watcher.models import User
from django.contrib.auth.hashers import make_password

from django.utils import timezone

from datetime import datetime

import stripe
import stripe.error


__all__ = ["UserSerializer"]


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    last_subscribe_till = serializers.SerializerMethodField()

    def get_last_subscribe_till(self, instance):
        last_subscribe = instance.latest_created_subscribe()
        if last_subscribe is None:
            return

        # FIXME: logic in serializer is FFFFUUUUUUU
        if last_subscribe.till < timezone.now(): #  Logic for check subscribtion
            try:
                stripe_subscription = stripe.Subscription.retrieve(
                    last_subscribe.stripe_token
                )  # Find subscription in stripe
                till = datetime.fromtimestamp(
                    stripe_subscription.current_period_end
                )
                if till != last_subscribe.till:
                    last_subscribe.till = till
                    last_subscribe.save()
            except stripe.error.InvalidRequestError:
                pass

        return last_subscribe.till

    def update(self, instance, validated_data):
        if validated_data.get('password') is not None:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'username_blacklist',
            'timezone',
            'password',
            'is_staff',
            'is_subscriber',
            'last_subscribe_till'
        )
