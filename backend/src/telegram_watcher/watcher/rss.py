from telegram_watcher.models import Source
from telegram_watcher.models.message import Message

from django.conf import settings

from django.utils.timezone import datetime, timedelta

from time import sleep

from logging import getLogger
import pytz

import feedparser

from django.db.utils import IntegrityError

from time import mktime

__all__ = ("RSSWatcher",)


class RSSWatcher(object):
    def __init__(self, *args, **kwargs):
        self.logger = getLogger()

    def run(self):
        for source in Source.objects.filter(type="rss"):
            if not source.active:
                source.active = True
                source.save()
            p = feedparser.parse(source.link)
            for entry in p.entries:
                msg = self.entry_to_messages(entry)
                msg.source = source
                if Message.objects.filter(
                        source=source,
                        text=msg.text
                ).exists():
                    continue
                try:
                    msg.save()
                except IntegrityError as e:
                    self.logger.error(e)

    def entry_to_messages(self, entry):
        content_r = entry.get('content')
        if isinstance(content_r, list):
            content_join = []
            for c in content_r:
                if isinstance(c, dict):
                    content_join.append(c.get('value'))
            content = "\r\n".join(content_join) if any(content_join) else None
        else:
            content = None

        title = entry.get('title')
        if not title:
            title = None
        contents = filter(
            lambda c: c is not None,
            (
                title,
                content,
                entry.get('summary'),
                entry.get('link')
            )
        )
        message_text = "\r\n".join(
            contents
        )
        message_date = entry.get('published_parsed') or entry.get('updated_parsed')
        message_date = datetime.fromtimestamp(
            mktime(message_date)
        ).replace(tzinfo=pytz.UTC) or datetime.now()
        author = entry.get('author')
        return Message(
            text=message_text,
            date=message_date,
            username=author
        )

    def stop(self):
        pass
