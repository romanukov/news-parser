"""
Скрипт для запуска Twitter бота
"""
import logging
from django.conf import settings

from django.core.management.base import BaseCommand
from telegram_watcher.watcher import TwitterWatcher


class Command(BaseCommand):
    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)
        watcher = TwitterWatcher()
        watcher.run()
        watcher.stop()
