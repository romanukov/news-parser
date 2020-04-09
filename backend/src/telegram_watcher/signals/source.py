from django.db.models import signals
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from telegram_watcher.models import TelegramAccount, Source
channel_layer = get_channel_layer()

__all__ = "source_saved", "source_deleted"


@receiver(signals.post_save, sender=Source)
def source_saved(sender, instance, created, **kwargs):
    if created:
        if instance.type == "telegram":
            print("Telegram source created")
            TelegramAccount.subscribe(instance)
        elif instance.type == "twitter":
            async_to_sync(channel_layer.send)(
                "twitter_watcher",
                {
                    "type": "channel.join",
                    "link": instance.link,
                    "source_id": instance.id
                }
            )
    else:
        if instance.type == "telegram":
            async_to_sync(channel_layer.send)(
                f"telegram_watcher_{instance.account_id}",
                {
                    "type": "channel.load_old_messages",
                    "source_id": instance.id,
                    "store_days": instance.store_days
                }
            )
        elif instance.type == "twitter":
            async_to_sync(channel_layer.send)(
                "twitter_watcher",
                {
                    "type": "channel.load_old_messages",
                    "source_id": instance.id,
                    "link": instance.link,
                    "store_days": instance.store_days
                }
            )


@receiver(signals.post_delete, sender=Source)
def source_deleted(sender, instance, **kwargs):
    if instance.type == "telegram":
        if instance.account_id:
            async_to_sync(channel_layer.send)(
                "telegram_watcher_{}".format(instance.account_id),
                {
                    "type": "channel.leave",
                    "link": instance.link,
                    "source_id": instance.id
                }
            )
        else:
            pass
    elif instance.type == "twitter":
        async_to_sync(channel_layer.send)(
            "twitter_watcher",
            {
                "type": "channel.leave",
                "link": instance.link,
                "source_id": instance.id
            }
        )


@receiver(signals.post_delete, sender=Source)
def source_deleted(sender, instance, **kwargs):
    if instance.type == "telegram":
        if instance.account_id:
            async_to_sync(channel_layer.send)(
                "telegram_watcher_{}".format(instance.account_id),
                {
                    "type": "channel.leave",
                    "link": instance.link,
                    "source_id": instance.id
                }
            )
        else:
            pass
    elif instance.type == "twitter":
        async_to_sync(channel_layer.send)(
            "twitter_watcher",
            {
                "type": "channel.leave",
                "link": instance.link,
                "source_id": instance.id
            }
        )
