from threading import Thread

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import signals
from django.dispatch import receiver

from telegram_watcher.models import SourceGroup, FeedSource, Feed

__all__ = "source_group_change_sources",


def _source_group_change_sources(instance, pk_set):
    for pk in pk_set:
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


@receiver(signals.m2m_changed, sender=SourceGroup.sources.through)
def source_group_change_sources(
        sender,
        action,
        instance,
        reverse,
        model,
        pk_set,
        using,
        **kwargs
):
    """
    При изменении группы источников сигнал добавит ко всем фидам с которыми
    связана измененная новые источники и удалит старые.
    """
    # TODO разобраться что вообще с этой тонной сигналов просходит
    if action == "post_add":
        for pk in pk_set:
            for feed in instance.feeds.all():
                FeedSource.objects.create(
                    source_id=pk,
                    feed=feed
                )
    if action == "post_remove":
        FeedSource.objects.filter(
            source_id__in=pk_set,
            feed__source_groups=instance
        ).delete()
