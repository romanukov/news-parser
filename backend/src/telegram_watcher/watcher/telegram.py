from django.conf import settings
from logging import getLogger
from telethon import TelegramClient, events, utils, errors
from telethon.tl.functions.channels import (
    JoinChannelRequest,
    LeaveChannelRequest,
)
from telethon.tl.functions.messages import (
    ImportChatInviteRequest
)
from telethon.tl.types import PeerChannel, PeerChat
from telethon.utils import pack_bot_file_id, get_extension

from telethon import types
from datetime import datetime, timedelta

from channels.layers import get_channel_layer

import pytz
from app.env import env
from asyncio import sleep
from django.core.files import File
from telegram_watcher.models import TelegramAccount, Source, Message, Account, AccountException, MessageFile
import asyncio
from app.celery import app
from telethon.sessions import StringSession
import gc

from os import remove


__all__ = ("TelegramWatcher",)


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


class TelegramWatcher(object):
    @staticmethod
    def new(account_id, **kwargs):
        account = TelegramAccount.objects.get(pk=account_id)
        string_session = kwargs.get('string_session')
        if string_session is None:
            Account.objects.filter(id=account.account_ptr_id).update(
                runned=False
            )
        else:
            string_session = StringSession(string_session)
        client = TelegramClient(
            string_session or f"{account.phone}.session",
            settings.TELEGRAM_API_ID,
            settings.TELEGRAM_API_HASH,
        )

        return TelegramWatcher(client,
                               account)

    def __init__(self, client: TelegramClient, account):
        self.logger = getLogger()
        self.account = account
        self.client = client

        self.channel_layer = get_channel_layer()
        self.async_loop = asyncio.get_event_loop()
        self.async_loop.run_until_complete(self._client_init())
        self.sources = {}

    def _get_media_size(self, file):
        if isinstance(file, types.MessageMediaDocument):
            file = file.document
        elif isinstance(file, types.MessageMediaPhoto):
            file = file.photo
        return getattr(file, 'size', 0)

    def download_task(self, file_id, msg_id):
        media = self.async_loop.run_until_complete(
            self.client.download_media(
                file_id,
                f'./media/'
            )
        )
        with open(media, 'rb') as file:
            if media is not None:
                MessageFile(
                    file=File(
                        file,
                        f'{str(msg_id)}-{media.split("/")[-1]}'
                    ),
                    message_id=msg_id
                ).save()
                remove(media)

    def download_media(self, message, msg):
        """
        Метод создает задачу в celery для скачивания файла из сообщения
        :param message:
        :param msg:
        :return:
        """
        media = message.media
        if isinstance(message.media, types.MessageMediaWebPage):
            if isinstance(message.media.webpage, types.WebPage):
                media = message.media.webpage.photo
        if media is None:
            return
        # 1048576 bytes in megabyte
        file_size_bytes = self._get_media_size(media)
        media_size_mb = file_size_bytes / 1048576
        if media_size_mb > 10:
            msg.meta['big_file_size'] = sizeof_fmt(file_size_bytes)
            msg.save()
            return
        file_id = pack_bot_file_id(media)
        if file_id is not None:
            app.send_task(
                'attachements.tasks.telegram_attachement',
                args=[
                    self.account.pk,
                    self.string_session,
                    file_id,
                    msg.id,
                    get_extension(media)
                ],
                queue='attachements'
            )

    async def _client_init(self):
        await self.client.connect()
        is_user_authorized = await self.client.is_user_authorized()

        self.account.authorized = is_user_authorized
        self.string_session = StringSession.save(self.client.session)
        TelegramAccount.objects.filter(id=self.account.id).update(
            authorized=is_user_authorized
        )

    def run(self):
        if not self.account.authorized:
            raise AccountException('Account not authorized')
        Account.objects.filter(id=self.account.account_ptr_id).update(
            runned=True
        )
        self.client.add_event_handler(self.new_message_handler, events.NewMessage)
        self.async_loop.create_task(self.django_channel_listener())
        self.async_loop.run_until_complete(self.get_subscribed())
        self.logger.info(f'Telegram client for {self.account.phone} started')
        self.async_loop.run_forever()
        Account.objects.filter(id=self.account.account_ptr_id).update(
            runned=False
        )
        self.stop()

    def stop(self):
        self.client.disconnect()

    async def get_subscribed(self):
        self.logger.info("Get subscribed channels")
        dialogs = await self.client.get_dialogs()
        subscribed_to = {
            dialog.entity.id: getattr(dialog.entity, "username", None)
            for dialog in dialogs if dialog.entity.id != 777000
        }
        self.account.sources.all().update(active=False)
        self.logger.info(f"Telegram account actually have opened {len(subscribed_to)} dialogs")
        active_sources = []

        Source.objects.filter(external_id__in=subscribed_to.keys(), type="telegram").update(account=self.account)

        for source in self.account.sources.all():
            if (
                (
                    source.external_id and
                    source.external_id not in subscribed_to
                ) or
                (
                    source.external_id is None and
                    source.link not in subscribed_to.values()  # TG account not subscribed to source
                )
            ):
                subscribed = await self.subscribe_to(source)
                if not subscribed:
                    continue
            active_sources.append(source.id)
            if source.external_id is not None:
                subscribed_to[source.external_id] = source

        self.account.sources.filter(id__in=active_sources).update(active=True)

        for external_id, source in subscribed_to.items():
            if isinstance(source, str):
                try:
                    subscribed_to[external_id] = self.account.sources.get(link=source)
                    self.account.sources.filter(link=source).update(external_id=external_id)
                except Source.DoesNotExist:
                    try:
                        subscribed_to[external_id] = self.account.sources.get(external_id=external_id)
                    except Source.DoesNotExist:
                        if env("TELEGRAM_SYNC_SOURCES"):
                            self.logger.info(f"LeaveChannelRequest {source}")
                            try:
                                await self.client(LeaveChannelRequest(source))
                            except TypeError:
                                self.logger.error(f"LeaveChannelRequest for {source} failed")
            elif source is None:
                try:
                    subscribed_to[external_id] = self.account.sources.get(external_id=external_id)
                except Source.DoesNotExist:
                    pass

        for dialog in dialogs:
            # if env("TELEGRAM_SYNC_SOURCES"):
            #     if subscribed_to.get(dialog.entity.id) is None:
            #         self.logger.warning(f"{self.account.phone} subscribed to unknown channel {dialog.entity}")
            self.account.sources.filter(external_id=dialog.entity.id).update(
                name=getattr(dialog.entity, "title", None) or getattr(dialog.entity, "username", None)
            )
        self.sources = {
            external_id: source
            for external_id, source in subscribed_to.items() if isinstance(source, Source)
        }
        self.logger.info(f"Sources count: {len(subscribed_to)}")

    async def _code_request(self):
        phone_code_hash = (
            await self.client.send_code_request(self.account.phone)
        ).phone_code_hash
        TelegramAccount.objects.filter(
            id=self.account.id
        ).update(
            phone_code_hash=phone_code_hash
        )

    def code_request(self):
        return self.async_loop.run_until_complete(
            self._code_request()
        )

    async def _sign_in(self):
        try:
            await self.client.sign_in(self.account.phone, self.account.auth_code,
                                      phone_code_hash=self.account.phone_code_hash)
        except errors.BadRequestError:
            await self._code_request()
        is_user_authorized = await self.client.is_user_authorized()
        TelegramAccount.objects.filter(id=self.account.id).update(
            authorized=is_user_authorized
        )
        self.account.authorized = is_user_authorized
        return is_user_authorized

    def code_auth(self):
        return self.async_loop.run_until_complete(self._sign_in())

    def _join_link(self, link):
        if link.startswith("joinchat/"):
            self.logger.info(f"Join invite {link[9:]}")
            return self.client(ImportChatInviteRequest(link[9:]))
        return self.client(JoinChannelRequest(link))

    async def channel_leave(self, data):
        self.logger.info(f"Leave t.me/{data['link']}")
        return await self.client(JoinChannelRequest(data["link"]))

    async def channel_join(self, data):
        self.logger.info(f"Subscribe to t.me/{data['link']}")
        try:
            resp = await self._join_link(data["link"])
        except (
            errors.UsernameInvalidError,
            errors.UsernameNotOccupiedError,
            errors.BadRequestError,
            TypeError,
            AttributeError,
            ValueError
        ):
            self.logger.error(f"Can't subscribe to source {data['link']}")
            return
        except errors.FloodWaitError as e:
            print(f"Join flood error, sleep for {e.seconds}")
            await sleep(e.seconds + 10)
            return await self.channel_join(data)
        Source.objects.filter(id=data["source_id"]).update(
            active=True,
            external_id=resp.chats[0].id,
            name=getattr(resp.chats[0], "title", None) or getattr(resp.chats[0], "username", None)
        )
        self.logger.info(f"Subscribe to t.me/{data['link']} is success")

        self.sources[resp.chats[0].id] = self.account.sources.get(id=data["source_id"])
        self.async_loop.create_task(self.load_old_messages(
           {
               "source_id": data["source_id"]
           }
        ))

    async def subscribe_to(self, source: Source):
        try:
            resp = await self._join_link(source.link)
        except (
            errors.UsernameInvalidError,
            errors.UsernameNotOccupiedError,
            errors.BadRequestError,
            TypeError,
            AttributeError,
            ValueError
        ) as e:
            self.logger.warning(f"Can't subscribe to source {source.link}")
            self.logger.warning(e)
            Source.objects.filter(
                id=source.id
            ).update(
                active=False,
                account=None
            )
            return False
        except errors.FloodWaitError as e:
            self.logger.warning(f"Flood error, sleep for {e.seconds + 10} seconds")
            await sleep(e.seconds + 10)
            return await self.subscribe_to(source)
        Source.objects.filter(id=source.id).update(
            external_id=resp.chats[0].id
        )
        return True

    def _get_source(self, event):
        if isinstance(event._chat_peer, PeerChannel):
            external_id = event._chat_peer.channel_id
        elif isinstance(event._chat_peer, PeerChat):
            external_id = event._chat_peer.chat_id
        else:
            return
        source = self.sources.get(external_id)
        if isinstance(source, Source):
            return source
        self.logger.warning(f"{external_id} source not found {event._chat_peer}")
        return

    async def django_channel_listener(self):
        self.logger.info('Channels listened started')
        self.logger.info(self.channel_layer)
        while True:
            try:
                msg = await self.channel_layer.receive(f"telegram_watcher_{self.account.id}")
            except ConnectionError:
                self.channel_layer = get_channel_layer()
                continue
            self.logger.info('Worker get message')
            if msg["type"] == 'channel.join':
                self.async_loop.create_task(self.channel_join(msg))
            elif msg["type"] == 'channel.leave':
                self.async_loop.create_task(self.channel_leave(msg))
            elif msg["type"] == 'channel.load_old_messages':
                self.async_loop.create_task(self.load_old_messages(msg))
            elif msg["type"] == 'channel.load_lost_messages':
                self.async_loop.create_task(self.load_lost_messages(msg))
            elif msg["type"] == 'worker.die':
                self.async_loop.stop()
                await self.client.log_out()

    async def new_message_handler(self, event):
        self.logger.debug("Account get message")
        if event.text is None:
            return
        source = self._get_source(event)
        if source is None:
            return
        meta = {}
        if isinstance(event.message.media, types.MessageMediaWebPage):
            if isinstance(event.message.media.webpage, types.WebPage):
                wp = event.message.media.webpage
                preview_meta = {
                    'url': wp.url,
                    'display_url': wp.display_url,
                    'site_name': wp.site_name,
                    'title': wp.title,
                    'description': wp.description,
                    'author': wp.author,
                }
                meta['preview'] = preview_meta
        msg = Message.objects.create(
            source=source,
            text=event.text,
            username=utils.get_display_name(event.sender),
            internal_id=int(event.message.id),
            date=event.message.date.replace(tzinfo=pytz.UTC),
            meta=meta
        )

        self.download_media(event.message, msg)

        gc.collect()

    async def load_old_messages(self, data):
        # Get messages for STORE_MESSAGES period
        source = Source.objects.get(pk=data["source_id"])
        self.logger.info(f"Load old messages from {source.link}")
        store_days = data.get("store_days", source.store_days)
        last_msg_id = source.messages.order_by('date')[0].internal_id \
            if source.messages.exists() else None
        from_date = (datetime.utcnow() - timedelta(store_days)).replace(
            tzinfo=pytz.UTC
        )
        _msg_count = 0

        entity = source.link
        if entity.startswith('joinchat/'):
            if source.external_id:
                entity = source.external_id3
                self.logger.info(f"Source {source.id} entity is {entity}")

        async for message in self.client.iter_messages(
            entity,
            min_id=last_msg_id or 0,
        ):
            if message.message is None:
                continue
            msg_date = message.date.replace(tzinfo=pytz.UTC)
            if msg_date < from_date:
                break
            username = utils.get_display_name(message.sender)
            # Create message in database

            meta = {}

            if isinstance(message.media, types.MessageMediaWebPage):
                if isinstance(message.media.webpage, types.WebPage):
                    wp = message.media.webpage
                    preview_meta = {
                        'url': wp.url,
                        'display_url': wp.display_url,
                        'site_name': wp.site_name,
                        'title': wp.title,
                        'description': wp.description,
                        'author': wp.author,
                        'embed_url': wp.embed_url,
                        'embed_type': wp.embed_type,
                        'embed_width': wp.embed_width,
                        'embed_height': wp.embed_height,
                    }
                    meta['preview'] = preview_meta
            msg = Message(
                source=source,
                text=message.message,
                date=msg_date,
                username=username,
                meta=meta
            )
            msg.save()

            _msg_count += 1
            if _msg_count % 100 == 0:
                self.logger.info(f"Loaded {_msg_count} message from {source.link}, latest date {msg_date}")
                # FIXME: Not load media for history
        self.logger.info(f"Loaded all history from {source.link}")


    async def load_lost_messages(self, data):
        """
        :param data: {
            "source_id": 321,
            "store_days": ""
        }
        :return:
        """
        source = Source.objects.get(pk=data["source_id"])
        self.logger.info(f"Load old messages from {source.link}")
        from_date = (datetime.utcnow() - timedelta(2)).replace(
            tzinfo=pytz.UTC
        )
        _msg_count = 0

        entity = source.link
        if entity.startswith('joinchat/'):
            if source.external_id:
                entity = source.external_id
                self.logger.info(f"Source {source.id} entity is {entity}")

        async for message in self.client.iter_messages(entity):
            if message.message is None:
                continue
            msg_date = message.date.replace(tzinfo=pytz.UTC)
            if msg_date < from_date:
                break
            username = utils.get_display_name(message.sender)
            # Create message in database
            msg, created = Message.objects.get_or_create(
                source=source,
                text=message.message,
                date=msg_date,
                username=username
            )
            if not created:
                continue
            _msg_count += 1
            if _msg_count % 100 == 0:
                self.logger.info(f"Loaded {_msg_count} message from {source.link}")
        self.logger.info(f"Loaded all history from {source.link}")

