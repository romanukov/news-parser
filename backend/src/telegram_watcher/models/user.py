from django.contrib.auth.models import AbstractUser
from django.db import models

from .message import Message
from .source import Source
from django.utils.translation import gettext_lazy as _
import pytz
import stripe
import stripe.error
from django.utils import timezone


__all__ = ("User", "UserSource")


class User(AbstractUser):
    favorites = models.ManyToManyField(
        Message,
        blank=True,
        related_name="users_favorites"
    )
    username_blacklist = models.TextField(
        blank=True
    )
    sources = models.ManyToManyField(
        Source,
        blank=True,
        through="UserSource",
        related_name="users"
    )
    is_subscriber = models.BooleanField(
        default=False
    )
    stripe_token = models.CharField(max_length=4096, null=True, blank=True)
    timezone = models.CharField(
        max_length=255,
        choices=(
            ('Etc/GMT-14', 'GMT-14'),
            ('Etc/GMT-13', 'GMT-13'),
            ('Etc/GMT-12', 'GMT-12'),
            ('Etc/GMT-11', 'GMT-11'),
            ('Etc/GMT-10', 'GMT-10'),
            ('Etc/GMT-9', 'GMT-9'),
            ('Etc/GMT-8', 'GMT-8'),
            ('Etc/GMT-7', 'GMT-7'),
            ('Etc/GMT-6', 'GMT-6'),
            ('Etc/GMT-5', 'GMT-5'),
            ('Etc/GMT-4', 'GMT-4'),
            ('Etc/GMT-3', 'GMT-3'),
            ('Etc/GMT-2', 'GMT-2'),
            ('Etc/GMT-1', 'GMT-1'),
            ('Etc/GMT-0', 'GMT-0'),
            ('Etc/GMT+0', 'GMT+0'),
            ('Etc/GMT+1', 'GMT+1'),
            ('Etc/GMT+10', 'GMT+10'),
            ('Etc/GMT+11', 'GMT+11'),
            ('Etc/GMT+12', 'GMT+12'),
            ('Etc/GMT+2', 'GMT+2'),
            ('Etc/GMT+3', 'GMT+3'),
            ('Etc/GMT+4', 'GMT+4'),
            ('Etc/GMT+5', 'GMT+5'),
            ('Etc/GMT+6', 'GMT+6'),
            ('Etc/GMT+7', 'GMT+7'),
            ('Etc/GMT+8', 'GMT+8'),
            ('Etc/GMT+9', 'GMT+9'),
        ),
        default='Etc/GMT+0'
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def sources_list(self):
        return self.sources.all().values_list('id', flat=True)

    def check_subscribe(self):
        return (
            not self.is_subscriber or
            self.subscriptions.filter(till__gte=timezone.now()).exists()
        )

    def latest_created_subscribe(self):
        return self.subscriptions.order_by('-id').first()

    def get_or_create_stripe_customer(self, checkout_token=None):
        if not self.is_subscriber or \
                (self.stripe_token is None and checkout_token is None):
            return None, False
        if self.stripe_token is not None:
            try:
                customer = stripe.Customer.retrieve(self.stripe_token)
                if checkout_token is not None:
                    customer.source = checkout_token
                    customer.save()
                return customer, False
            except stripe.error.InvalidRequestError:
                if checkout_token is not None:
                    customer = stripe.Customer.create(
                        email=self.email,
                        source=checkout_token
                    )
                    self.stripe_token = customer.get('id')
                    self.save()
                    return customer, True
                return None
        if checkout_token is not None:
            customer = stripe.Customer.create(
                email=self.email,
                source=checkout_token
            )
            self.stripe_token = customer.get('id')
            self.save()
            return customer, True
        return None, False


    def stripe_get_subscriptions(self, plan=None):
        return stripe.Subscription.list(customer=self.stripe_token, plan=plan)


    @property
    def blacklist(self):
        blacklist_users = str(self.username_blacklist).split("\r\n")
        if "" in blacklist_users:
            blacklist_users.remove("")
        return blacklist_users

    def add_to_blacklist(self, author):
        blacklist_users = self.blacklist
        if author not in blacklist_users:
            blacklist_users.append(author)
        self.username_blacklist = "\r\n".join(blacklist_users)

    def remove_from_blacklist(self, author):
        blacklist_users = self.blacklist
        if author in blacklist_users:
            blacklist_users.remove(author)
        self.username_blacklist = "\r\n".join(blacklist_users)


class UserSource(models.Model):
    source = models.ForeignKey(
        Source,
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.source.link

    @property
    def link(self):
        return self.source.link

    @property
    def type(self):
        return self.source.type

    @property
    def language(self):
        return self.source.language

    @property
    def store_days(self):
        return self.source.store_days

    @property
    def type_link_mask(self):
        return self.source.type_link_mask

    class Meta:
        verbose_name = "My Source"
        unique_together = (('source', 'user'),)
