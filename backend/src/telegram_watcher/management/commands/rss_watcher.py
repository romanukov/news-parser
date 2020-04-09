"""
Скрипт для запуска RSS бота
"""
import logging
from django.conf import settings

from django.core.management.base import BaseCommand
from telegram_watcher.watcher import RSSWatcher


class Command(BaseCommand):
    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)
        watcher = RSSWatcher()
        watcher.run()
        watcher.stop()
