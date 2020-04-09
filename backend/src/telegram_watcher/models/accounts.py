from django.db import models

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .source import Source
from logging import info

__all__ = ['Account', 'TelegramAccount', 'AccountException']


class AccountException(Exception):
    pass


class Account(models.Model):
    sources_restrictor = 2

    runned = models.BooleanField(default=False)
    authorized = models.BooleanField(default=False)

    @classmethod
    def batch_subscribe(cls, sources):
        channel_layer = get_channel_layer()
        accounts_queryset = list(cls.objects.all())
        if len(accounts_queryset) == 0:
            raise AccountException("Please, create at least one account")
        for source in sources:
            account = max(
                accounts_queryset,
                key=lambda acc: cls.sources_restrictor - acc.amount_sources()
            )
            if cls.sources_restrictor == account.amount_sources():
                raise AccountException("Haven't free accounts")
            Source.objects.filter(id=source.id).update(
                account=account
            )

            async_to_sync(channel_layer.send)(
                f"telegram_watcher_{account.id}",
                {
                    "type": "channel.join",
                    "link": source.link,
                    "source_id": source.id
                }
            )
        return account

    @classmethod
    def _get_account_for_subscribe(cls):
        accounts_queryset = cls.objects.filter(runned=True)
        if len(accounts_queryset) == 0:
            raise AccountException("Please, create at least one account")
        account_for_subscribe = max(
            accounts_queryset,
            key=lambda acc: cls.sources_restrictor - acc.amount_sources()
        )
        if cls.sources_restrictor - account_for_subscribe.amount_sources() == 0:
            raise AccountException("Haven't free accounts")
        return account_for_subscribe

    @classmethod
    def subscribe(cls, source):
        print("Account subscribe")
        channel_layer = get_channel_layer()
        account = cls._get_account_for_subscribe()
        Source.objects.filter(id=source.id).update(
            account=account
        )
        info("Source subscribed")

        async_to_sync(channel_layer.send)(
            f"telegram_watcher_{account.id}",
            {
                "type": "channel.join",
                "link": source.link,
                "source_id": source.id
            }
        )
        return account

    def __str__(self):
        return f'Account {self.id}'

    def amount_sources(self):
        return self.sources.all().count()

    @property
    def sources_count(self):
        return self.amount_sources()


class TelegramAccount(Account):
    sources_restrictor = 480
    phone = models.CharField(
        max_length=12,
        null=True,
        blank=True
    )
    auth_code = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Auth code'
    )
    phone_code_hash = models.CharField(
        max_length=2048,
        blank=True,
        default=""
    )

    def __str__(self):
        return f'Account {self.account_ptr_id}'

    class Meta:
        verbose_name = "Telegram Account"
