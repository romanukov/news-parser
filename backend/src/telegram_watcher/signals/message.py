from asgiref.sync import async_to_sync
from django.db import IntegrityError
from django.db.models import signals
from django.dispatch import receiver

from telegram_watcher.models import Message, FeedSource, FeedMessage, MessageFile
from channels.layers import get_channel_layer
from asyncio import _get_running_loop

channel_layer = get_channel_layer()

__all__ = "message_saved", "feed_message_saved"


@receiver(signals.post_delete, sender=MessageFile)
def submission_delete(sender, instance, **kwargs):
    instance.file.delete(False)


@receiver(signals.post_save, sender=Message)
def message_saved(sender, instance, created, **kwargs):
    if created:
        for feed_source in FeedSource.objects.filter(source=instance.source).all().select_related('feed'):
            _feed = feed_source.feed
            if not any(_feed.words):
                try:
                    FeedMessage.objects.create(
                        feed=_feed,
                        message=instance,
                        feed_source=feed_source
                    )
                except IntegrityError:
                    pass
            else:
                for msg in Message.fulltext_search(
                    _feed.fulltext_query,
                    Message.objects.filter(pk=instance.id)
                ):
                    FeedMessage.objects.create(
                        feed=_feed,
                        message=msg,
                        feed_source=feed_source
                    )


@receiver(signals.post_save, sender=FeedMessage)
def feed_message_saved(sender, instance, created, **kwargs):
    if created:
        feed = instance.feed
        feed.new_messages += 1
        feed.save()
        if feed.user_id is not None:
            usergroup = "%d.user" % feed.user_id
            loop =_get_running_loop()
            if loop is None:
                async_to_sync(channel_layer.group_send)(
                    usergroup,
                    {"type": "feed.new_message", "feed": feed.id}
                )
            else:
                loop.create_task(channel_layer.group_send(
                    usergroup,
                    {"type": "feed.new_message", "feed": feed.id}
                ))
