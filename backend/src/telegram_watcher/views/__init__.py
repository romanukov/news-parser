from .feed import *
from .message import *
from .user import *
from .source import *
from .stripe import *


from django.views.generic import TemplateView
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from telegram_watcher.models import Source, Message


class WorkerStatsAdminView(TemplateView):
    template_name = 'worker_stats.html'

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'rss_worker': {
                'last_message': Message.objects.filter(
                    source__type='rss').order_by('-date').first()
            },
            'telegram_worker': {
                'last_message': Message.objects.filter(
                    source__type='telegram').order_by('-date').first()
            },
            'twitter_worker': {
                'last_message': Message.objects.filter(
                    source__type='twitter').order_by('-date').first()
            }
        })
        return context
