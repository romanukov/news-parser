from telegram_watcher.models import TelegramAccount
from django.db.models import signals
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from telegram_watcher.tasks import telegram_spawner

channel_layer = get_channel_layer()

__all__ = "telegram_account_saved",


@receiver(signals.post_save, sender=TelegramAccount)
def telegram_account_saved(sender, instance, created, **kwargs):
    if not instance.runned:
        telegram_spawner.delay(instance.id)


@receiver(signals.post_delete, sender=TelegramAccount)
def telegram_account_deleted(sender, instance, **kwargs):
    async_to_sync(channel_layer.send)(
        f"telegram_watcher_{instance.id}",
        {
            "type": "worker.die",
        }
    )
