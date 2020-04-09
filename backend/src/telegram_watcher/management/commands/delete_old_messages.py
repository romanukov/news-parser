"""
Script for deleting old messages
"""
import logging
from django.core.management.base import BaseCommand
from telegram_watcher.models import Source
from datetime import timedelta
from django.utils import timezone
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)
        sources = Source.objects.all()
        for source in sources:
            if not source.store_days:
                continue
            source.messages.filter(
                users_favorites__isnull=True,
                date__lte=timezone.now() - timedelta(source.store_days)
            ).delete()
