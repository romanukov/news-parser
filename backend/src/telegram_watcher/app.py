from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class TelegramWatcherConfig(AppConfig):
    name = 'telegram_watcher'
    verbose_name = _('Telegram Watcher')

    def ready(self):
        from . import signals