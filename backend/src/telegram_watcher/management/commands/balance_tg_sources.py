"""
Script for deleting old messages
"""
import logging
from django.core.management.base import BaseCommand
from telegram_watcher.models import Source, TelegramAccount
from datetime import timedelta
from time import sleep
from django.utils import timezone
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)
        sources = Source.objects.filter(account__runned=False)
        print(f'Dead sources: {sources.count()}')
        for source in sources:
            print(f'Subscribe source: {source.link}')
            TelegramAccount.subscribe(source)
            sleep(20)
