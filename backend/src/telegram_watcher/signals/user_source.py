from django.db.models import signals
from django.dispatch import receiver

from telegram_watcher.models import UserSource, Feed, FeedSource, Source

__all__ = "deleted_mysource", "save_mysource"


@receiver(signals.post_delete, sender=UserSource)
def deleted_mysource(sender, instance, **kwargs):
    try:
        source = instance.source
        for i in Feed.objects.filter(user=instance.user).all():
            FeedSource.objects.filter(feed=i, source=source).delete()
    except Source.DoesNotExist:
        return
    if not instance.source.users.exists():
        instance.source.delete()


@receiver(signals.post_save, sender=UserSource)
def save_mysource(sender, instance, created, **kwargs):
    # Add to feeds with "new_sources" option
    if created:
        for i in Feed.objects.filter(user=instance.user, new_sources=True).all():
            FeedSource(feed=i, source=instance.source).save()