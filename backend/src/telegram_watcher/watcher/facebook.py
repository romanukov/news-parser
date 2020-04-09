from telethon import TelegramClient, events, utils
from telethon.tl.functions.channels import (
    JoinChannelRequest, LeaveChannelRequest, GetMessagesRequest)

from telegram_watcher.models import Source
from telegram_watcher.models.message import Message

from django.conf import settings

from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta

from asyncio import get_event_loop
from time import sleep
from channels.layers import get_channel_layer

from logging import getLogger

from channels.db import database_sync_to_async

import feedparser

from time import mktime

__all__ = ("FacebookWatcher",)


class FacebookWatcher(object):
    def __init__(self, *args, **kwargs):
        self.logger = getLogger()
        self.graph_api = facebook.GraphAPI(settings.FACEBOOK["TOKEN"])

    def run(self):
        self.logger.info("Started facebook watcher")
        page = self.graph_api.get_object("bitcoin", fields=['name'])
        print(page)

    def stop(self):
        pass