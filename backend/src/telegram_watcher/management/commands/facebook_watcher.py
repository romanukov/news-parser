"""
Скрипт для запуска Facebook бота
"""
import logging
from django.conf import settings

from django.core.management.base import BaseCommand
from telegram_watcher.watcher import FacebookWatcher


class Command(BaseCommand):
    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)
        watcher = FacebookWatcher()
        watcher.run()
        watcher.stop()
