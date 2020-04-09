from django.db import models
from pycountry import languages
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()


__all__ = ("Source", "SourceGroup")


class SourceGroup(models.Model):
    name = models.CharField(max_length=255)

    sources = models.ManyToManyField(
        "Source",
        blank=True,
        related_name="source_groups"
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Source(models.Model):
    type = models.CharField(
        choices=[
            ('telegram', 'Telegram'),
            ('rss', 'RSS'),
            ('twitter', 'Twitter'),
        ],
        max_length=256
    )  # Type of source. Also must be setted in admin/source
    link = models.CharField(
        max_length=512
    )
    name = models.CharField(
        max_length=1024,
        blank=True,
        null=True
    )
    language = models.CharField(
        max_length=256,
        default="eng",
        choices=[("NONE", "Select language...")] + [
            (lang[0], lang[1])
            for lang in (
                ('ENG', 'English'),
                ('RUS', 'Russian'),
                ('CHN', 'Chinese'),
                ('KOR', 'Korean'),
                ('JAP', 'Japanese')
            )
        ]
    )
    external_id = models.BigIntegerField(null=True, blank=True)
    active = models.BooleanField(default=False)
    store_days = models.IntegerField(default=settings.DEFAULT_STORE_DAYS)
    account = models.ForeignKey(
        "Account",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='sources'
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def load_lost_messages(self):
        async_to_sync(channel_layer.send)(
            f"telegram_watcher_{self.account_id}",
            {
                "type": "channel.load_lost_messages",
                "source_id": self.id,
                "store_days": self.store_days
            }
        )

    def __str__(self):
        return f'{self.pk}. {self.link}\n{self.type}\n{self.name}'

    class Meta:
        verbose_name = "System Source"
        unique_together = (('type', 'link'),)