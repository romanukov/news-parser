from django.db.models import signals
from django.dispatch import receiver

from telegram_watcher.models import FeedSource, Message, FeedMessage

__all__ = "feed_change_sources",


@receiver(signals.post_save, sender=FeedSource)
def feed_change_sources(sender, instance, **kwargs):
    feed = instance.feed
    if not any(feed.words):
        for msg in Message.objects.filter(source_id=instance.source_id):
            FeedMessage.objects.create(
                feed=feed,
                message=msg,
                feed_source=instance
            )
        return

    messages = Message.fulltext_search(
        feed.fulltext_query,
        Message.objects.filter(source_id=instance.source_id)
    )
    for msg in messages:
        FeedMessage.objects.create(
            feed=feed,
            message=msg,
            feed_source=instance
        )