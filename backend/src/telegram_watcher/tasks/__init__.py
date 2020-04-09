from celery.signals import worker_ready
from celery.task import task

from django.conf import settings
from app.env import env
from telegram_watcher.watcher import TwitterWatcher, TelegramWatcher, RSSWatcher
from telethon.client import TelegramClient
from telethon.sessions import StringSession
import asyncio
from django.core.files import File
from django.utils.timezone import now
from telegram_watcher.models import MessageFile
from os import remove
from django.core.mail import send_mail


@task(name='twitter.tasks.twitter_spawner',
      queue='twitter',
      autoretry_for=(Exception,),
      retry_kwargs={'max_retries': 3},)
def twitter_spawner():
    watcher = TwitterWatcher()
    try:
        watcher.run()
    except Exception as e:
        print(e)
        watcher.stop()
        twitter_spawner.delay()
    else:
        watcher.stop()


@task(name='rss.tasks.rss_spawner',
      queue='rss',
      autoretry_for=(Exception,),
      retry_kwargs={'max_retries': 3},)
def rss_spawner():
    return RSSWatcher().run()


@task(name='telegram.tasks.telegram_spawner',
      queue='telegram',
      autoretry_for=(Exception,),
      retry_kwargs={'max_retries': 3},)
def telegram_spawner(account_id):
    # This task create and run telegram watcher
    watcher = TelegramWatcher.new(account_id)
    # If watcher is not authorized
    if not watcher.account.authorized:
        if watcher.account.auth_code is None:
            # Send code and die
            watcher.code_request()
            watcher.stop()
            return
        # Code presented, try to auth
        authorized = watcher.code_auth()
        if not authorized:
            watcher.stop()
            return
    watcher.run()
    watcher.stop()

@task(name='telegram.tasks.telegram_tester',
      queue='telegram',)
def telegram_tester():
    # This task create and run telegram watcher
    from telegram_watcher.models import TelegramAccount, Message
    alarm_date = now() - timedelta(minutes=10)
    for acc in TelegramAccount.objects.filter(runned=True):
        if not Message.objects.filter(
                source__account=acc,
                created__gt=alarm_date
        ).exists():
            send_mail(
                f"Telegram account {acc.id} is forgot messages in down",
                f"Telegram account {acc.id} is forgot messages in down",
                env("EMAIL_FROM"),
                ['f42.dobro@gmail.com']
            )

@task(name='attachements.tasks.telegram_attachement',
      queue='attachements',
      autoretry_for=(Exception,),
      retry_kwargs={'max_retries': 3},
      retry_backoff=True)
def telegram_attachement(account_id, string_session, file_id, msg_id, ext):
    """
    Задача для скачивания файла из телеграмма
    :param account_id: id аккаунта в системе подписанного на источник
    :param string_session: переданная строкой сессия телеграмма
    :param file_id: id файла resolve_bot_file_id
    :param msg_id: id сообщения
    :param ext:
    :return:
    """
    # Асинхронный луп нужен для запуска методов TelegramClient из либы telethon
    event_loop = asyncio.new_event_loop()
    telegram_client = TelegramClient(
        StringSession(string_session),
        settings.TELEGRAM_API_ID,
        settings.TELEGRAM_API_HASH,
        loop=event_loop
    )
    event_loop.run_until_complete(
        telegram_client.connect()
    )
    media = event_loop.run_until_complete(
        telegram_client.download_media(
            file_id,
            f'./media/'
        )
    )
    if media is None:
        return
    fname = f'{str(msg_id)}-{media.split("/")[-1]}'
    if not fname.endswith('jpg'):
        fname = f'{fname}{ext}'
    with open(media, 'rb') as file:
        MessageFile(
            file=File(
                file,
                fname
            ),
            message_id=msg_id
        ).save()
        remove(media)
    event_loop.close()


@worker_ready.connect
def up_watchers(sender, *args, **kwargs):
    if 'telegram' in sender.task_consumer._queues:
        from telegram_watcher.models import TelegramAccount
        if env("RUN_TELEGRAM_WORKER"):
            for account in TelegramAccount.objects.all():
                telegram_spawner.delay(account.id)
    if 'twitter' in sender.task_consumer._queues:
        if env("RUN_TWITTER_WORKER"):
            twitter_spawner.delay()
