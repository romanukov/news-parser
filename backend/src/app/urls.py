"""src URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.admin import site
from django.urls import path, include, re_path
import telegram_watcher.views as tgwatcher_views
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from telegram_watcher.admin.source_ajax import SourceAjaxView

adminurls = [
    path(r'gotoadmin/worker_stats/', tgwatcher_views.WorkerStatsAdminView.as_view()),
    re_path(r'^gotoadmin/source/(?P<id>[0-9]+)/$', SourceAjaxView.as_view()),
    path(r'gotoadmin/', site.urls),
]

urlpatterns = [
    path(r'api/', include('telegram_watcher.urls')),
] + adminurls
