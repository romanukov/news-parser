from threading import Thread

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import signals
from django.dispatch import receiver

from telegram_watcher.models import SourceGroup, FeedSource, Feed

__all__ = "feed_change_source_group",


def _feed_change_source_group(instance, pk_set):
    for pk in pk_set:
        # fixme - может быть это лучше сделать транзакцией, очень страное место
        source_group = SourceGroup.objects.get(pk=pk)
        for source in source_group.sources.all():
            fs = FeedSource(source=source, feed=instance)
            try:
                fs.validate_unique()
            except ValidationError:
                continue
            try:
                fs.save()
            except IntegrityError:
                continue


@receiver(signals.m2m_changed, sender=Feed.source_groups.through)
def feed_change_source_group(sender, action, instance, reverse, model, pk_set, using, **kwargs):
    if action == "post_add":
        t = Thread(target=_feed_change_source_group, args=(instance, pk_set))
        t.daemon = True
        t.start()