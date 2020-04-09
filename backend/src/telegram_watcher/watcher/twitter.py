from django.conf import settings
from django.utils import timezone
import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream, API
from logging import getLogger
import logging
import json
from datetime import datetime, timedelta
from channels.layers import get_channel_layer
from time import sleep
from telegram_watcher.models import Source, Message
import pytz
import asyncio
import requests
from lxml import html
import multiprocessing
from concurrent.futures import ThreadPoolExecutor


__all__ = ("TwitterWatcher",)


_log = logging.getLogger(__name__)


class TwitterWatcher(StreamListener):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api)
        self.logger = getLogger()
        self.logger.info('Initialize TwitterWatcher')
        auth = OAuthHandler(
            settings.TWITTER_CONSUMER_KEY,
            settings.TWITTER_CONSUMER_SECRET
        )
        auth.set_access_token(
            settings.TWITTER_ACCESS_TOKEN,
            settings.TWITTER_ACCESS_TOKEN_SECRET
        )
        self.api = API(
            auth,
            wait_on_rate_limit=True,
            wait_on_rate_limit_notify=True
        )
        self.channel_layer = get_channel_layer()
        self.stream = Stream(
            auth,
            listener=self,
        )
        self._sources = {}
        self._load_sources()
        self.pool = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count())

        self.async_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.async_loop)

    def _load_sources(self):
        self.logger.info('Twitter load sources')
        Source.objects.filter(type="twitter").update(active=False)
        sources = Source.objects.filter(type="twitter")
        active_sources = []
        for source in sources:
            if source.external_id is None or source.name is None:
                twitter_user = self._get_user(source.link)
                twitter_id = getattr(twitter_user, "id", None)
                twitter_name = getattr(twitter_user, "name", None)
                Source.objects.filter(id=source.id).update(
                    external_id=twitter_id,
                    name=twitter_name
                )
            else:
                twitter_id = source.external_id
            if twitter_id is None:
                self.logger.info(
                    "Cant find twitter id for source %s" % source.link)
                continue
            active_sources.append(source.id)
            self._sources.update({twitter_id: source.id})
        Source.objects.filter(type="twitter", id__in=active_sources).update(
            active=True
        )
        # for _twitter_id in self._sources:
        #     self.get_old_messages(_twitter_id)

    def _get_user(self, source_link):
        try:
            user = self.api.get_user('@{}'.format(source_link))
        except tweepy.error.TweepError as ex:
            return
        return user

    async def django_channel_listener(self, name):
        self.logger.info('Channels listened started')
        self.logger.info(self.channel_layer)
        try:
            while True:
                try:
                    msg = await self.channel_layer.receive(name)
                except ConnectionError as e:
                    self.logger.warning(
                        'Django channels listener raises ConnectionError'
                    )
                    self.logger.error(e)
                    continue
                if msg["type"] == 'channel.join':
                    self.logger.info('Twitter watcher subscribe to source')
                    twitter_user = self._get_user(msg["link"])
                    twitter_id = getattr(twitter_user, "id", None)
                    twitter_name = getattr(twitter_user, "name", None)
                    Source.objects.filter(id=msg["source_id"]).update(
                        active=True,
                        name=twitter_name,
                        external_id=twitter_id
                    )
                    if twitter_id is None:
                        self.logger.info(
                            "Cant find twitter id for source %s" % msg["link"]
                        )
                        continue
                    self._sources.update({twitter_id: msg["source_id"]})
                    self.stream_follow_sources()
                    # self.reconnect()
                    self.async_loop.run_in_executor(self.pool,
                                                    self.get_old_messages,
                                                    twitter_id)

                elif msg["type"] == 'channel.leave':
                    print('Leave link {}'.format(msg.get('link')))
                    for tw_id, s_id in self._sources.items():
                        if s_id != msg["source_id"]:
                            continue
                        self._sources.pop(tw_id)
                        self.stream_follow_sources()
                        break
                    # self.reconnect()
        except Exception as e:
            self.logger.warning(
                'Django channels listener raises unknown Exception'
            )
            self.logger.error(e)
            self.async_loop.create_task(
                self.django_channel_listener('twitter_watcher')
            )

    def get_old_messages(self, twitter_id):
        source_id = self._sources.get(twitter_id)
        if source_id is None:
            return
        source = Source.objects.get(pk=source_id)
        if source.messages.exists():
            dead_date = source.messages.last().date
        else:
            dead_date = timezone.now() - timedelta(source.store_days)

        for status in tweepy.Cursor(self.api.user_timeline, id=twitter_id).items():
            if status.created_at.replace(tzinfo=pytz.UTC) < dead_date:
                self.logger.info("Loaded messages for %s" % str(twitter_id))
                break
            message = Message(
                date=status.created_at.replace(tzinfo=pytz.UTC),
                username=status.user.screen_name if status.user else None,
                text=status.text,
                source_id=source_id,
                meta=self._create_meta(status._json.get("entities", {})),
                internal_id=status._json.get("id"),
            )
            message.save()

    @property
    def stream_follow(self):
        return self.stream.body['follow']

    def stream_follow_sources(self):
        if self.stream.body is not None:
            self.stream.body['follow'] = u','.join(map(str, self._sources.keys()))
            self.logger.info('Now stream follow %s' % self.stream_follow)

    def run(self):
        self.logger.info("Started twitter watcher")
        twitter_acc = self.api.me()
        logging.info("Account id: %s" % twitter_acc.id)
        logging.info("Account screen name: %s" % twitter_acc.screen_name)
        logging.info("Account name: %s" % twitter_acc.name)
        logging.info("Create django channel listener")
        self.async_loop.create_task(
            self.django_channel_listener('twitter_watcher')
        )
        self.async_loop.run_in_executor(self.pool, self.twitter_listener)
        self.stream_follow_sources()

        try:
            self.async_loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            logging.info("Disconnect twitter watcher")
            self.stream.disconnect()
        return

    def twitter_listener(self):
        self.logger.info('Running stream loop')
        try:
            self.stream.filter(map(str, self._sources.keys()))
        except Exception as e:
            self.logger.info('Reconnect stream loop')
            # Reconnect
            self.logger.warning(e)
            self.stream.disconnect()
            self.async_loop.run_in_executor(self.pool, self.twitter_listener)
            self.stream_follow_sources()

    def stop(self):
        pass

    def on_error(self, status):
        pass

    def on_exception(self, status):
        pass

    def _create_meta(self, entities):
        meta = {}
        if 'media' in entities:
            meta['media'] = entities['media']

        if 'urls' in entities:
            for url in entities['urls']:
                uri = url.get('expanded_url', url.get('display_url'))
                if uri is None:
                    break
                try:
                    r = requests.get(uri)
                except requests.exceptions.RequestException:
                    break
                if r.status_code != 200:
                    break
                parsed_html = html.fromstring(r.text)
                og_meta = {}
                for tag in parsed_html.iter('meta'):
                    name = tag.attrib.get('name', "")
                    property = tag.attrib.get('property', "")
                    content = tag.attrib.get('content', tag.text)
                    if property == 'og:title':
                        og_meta['title'] = content
                    if property == 'og:description':
                        og_meta['description'] = content
                    if name == 'og:description':
                        if 'description' not in og_meta:
                            og_meta['description'] = content
                    if property == 'og:url':
                        og_meta['url'] = content
                    if property == 'og:site_name':
                        og_meta['site_name'] = content
                    if property == 'og:image':
                        og_meta['image'] = content
                    if name == 'author':
                        og_meta['author'] = content
                meta['preview'] = {
                    'url': og_meta.get('url', uri),
                    'display_url': og_meta.get('url', uri),
                    'site_name': og_meta.get('site_name', ''),
                    'title': og_meta.get('title', ''),
                    'description': og_meta.get('description', ''),
                    'author': og_meta.get('author', ''),
                    'image': og_meta.get('image', ''),
                }
                break
        return meta

    def on_data(self, data):
        data_json = json.loads(data)
        if not data_json.get("delete"):
            message_user = data_json.get("user")
            if message_user is None:
                return
            source_id = self._sources.get(message_user.get("id"))
            if source_id is None:
                return
            data_date = data_json.get("created_at")
            date = datetime.strptime(data_date, "%a %b %d %H:%M:%S +0000 %Y") \
                if data_date else timezone.now()
            message = Message(
                date=date.replace(tzinfo=pytz.UTC),
                username=message_user.get(
                    "screen_name"
                ) if message_user else None,
                text=data_json.get("text"),
                source_id=source_id,
                internal_id=data_json.get("id"),
                meta=self._create_meta(data_json.get("entities", {}))
            )
            message.save()
        return True

    def on_connect(self):
        pass
