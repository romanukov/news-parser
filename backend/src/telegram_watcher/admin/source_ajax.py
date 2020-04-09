from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from telegram_watcher.models import Source
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator


@method_decorator(user_passes_test(lambda user: user.is_superuser), name='dispatch')
class SourceAjaxView(View):
    def get(self, request, id):
        source = get_object_or_404(Source, pk=id)
        return JsonResponse({"id": source.id, "link": source.link, "type": source.type})