from django.contrib.auth.models import Group
from django.db.models import signals
from django.dispatch import receiver

from telegram_watcher.models import User, Feed

__all__ = "user_saved",


@receiver(signals.post_save, sender=User)
def user_saved(sender, instance: User, **kwargs):
    try:
        group = Group.objects.get(name="default")
        instance.groups.add(group)
    except Group.DoesNotExist:
        print("Warning, default group does not exist")
    instance.m2m_feeds.add(*list(Feed.objects.filter(pre_defined=True)))
