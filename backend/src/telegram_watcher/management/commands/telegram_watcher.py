"""
Скрипт для запуска Telegram бота
"""
import logging
from django.conf import settings

from django.core.management.base import BaseCommand
from telegram_watcher.watcher import TelegramWatcher


class Command(BaseCommand):
    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)
        watcher = TelegramWatcher.new()
        watcher.run()
        watcher.stop()
