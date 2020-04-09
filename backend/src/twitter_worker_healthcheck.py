#!/usr/bin/env python

"""
This script twitter workers use as healthcheck for docker-containers.
"""

from gevent import monkey; monkey.patch_all()
from os import environ
import django
from sys import exit


environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "app.settings"
)
django.setup()

from app.celery import app
from telegram_watcher.tasks import twitter_spawner

# Work for only one telegram worker

worker_name = f'celery@{environ.get("HOSTNAME")}'
inspector = app.control.inspect([worker_name])
active_tasks = inspector.active().get(worker_name)

active_accounts = {int(task['args'][1:-1].split(',')[0])
                   for task in active_tasks
                   if task['name'] == 'twitter.tasks.twitter_spawner'}

if len(active_accounts) == 0:
    twitter_spawner.delay()

exit(0)
