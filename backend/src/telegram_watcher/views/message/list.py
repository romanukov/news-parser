from datetime import timedelta
from dateparser import parse

from django.db import models

from rest_framework import generics, views

from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination, replace_query_param

from telegram_watcher.models import Message, Feed
from telegram_watcher.serializers import *

from ..mixins.timezone import APIUserTimezone
from django.utils.timezone import now

from ...permissions import IsSubscribedPermission

__all__ = [
    "MessageList",
    "MessageDetail",
    "FeedMessageList",
    "FavoritesMessageList",
    "FailOverMessageList",
    "MessageCount"
]


class LimitOffsetPaginationWithoutCount(LimitOffsetPagination):
    def paginate_queryset(self, queryset, request, view=None):
        self.count = 0
        self.limit = self.get_limit(request)
        if self.limit is None:
            return None
        self.offset = self.get_offset(request)
        self.request = request
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True
        return list(queryset[self.offset:self.offset + self.limit])

    def get_next_link(self):
        url = self.request.build_absolute_uri()
        url = replace_query_param(url, self.limit_query_param, self.limit)

        offset = self.offset + self.limit
        return replace_query_param(url, self.offset_query_param, offset)


class MessageCount(views.APIView):
    permission_classes = [IsSubscribedPermission]
    def get(self, request):
        count = Message.objects.filter(
            source_id__in=self.request.user.sources_list()
        ).count()
        return views.Response({"count": count})


class MessageDetail(APIUserTimezone, generics.RetrieveAPIView):
    permission_classes = [IsSubscribedPermission]
    serializer_class = MessageSerializer
    queryset = Message.objects.all()


class MessageList(APIUserTimezone, generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsSubscribedPermission]
    serializer_class = MessageSerializer
    pagination_class = LimitOffsetPaginationWithoutCount

    @property
    def _source(self):
        try:
            return int(self.request.query_params.get('source', None))
        except TypeError:
            return None

    @property
    def _date_from(self):
        return parse(self.request.query_params.get('date_from', ""))

    @property
    def _date_to(self):
        return parse(self.request.query_params.get('date_to', ""))

    def filter_queryset(self, queryset):
        q = queryset
        source = self._source
        if source is not None:
            q = q.filter(source_id=source)
        date_to = self._date_to
        date_from = self._date_from
        if date_from is not None:
            q = q.filter(date__gte=date_from)
        if date_to is not None:
            q = q.filter(date__lte=date_to + timedelta(1))
        return q

    def get_queryset(self):
        sources = list(self.request.user.sources_list())
        messages_qs = Message.objects.filter(
            source_id__in=sources
        )
        if messages_qs.exists():
            return (
                messages_qs
                .select_related(
                    'source',
                )
                .prefetch_related(
                    'duplicate__messages',
                    'files'
                )
                .annotate(
                    favorites=models.Case(
                        models.When(users_favorites__pk=self.request.user.pk,
                                    then=models.Value(True)),
                        default=models.Value(False),
                        output_field=models.BooleanField(),
                    )
                )
                .order_by('-date')
            )
        else:
            return Message.objects.none()


class FeedMessageList(MessageList):
    permission_classes = [IsSubscribedPermission]
    def __init__(self):
        super().__init__()
        self.feed = None

    def initial(self, request, *args, **kwargs):
        feed_id = self.kwargs.get("feed")
        try:
            self.feed = Feed.objects.filter(
                models.Q(user=self.request.user) |
                models.Q(users=self.request.user)
            ).get(pk=feed_id)
        except Feed.DoesNotExist:
            pass
        return super().initial(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["feed"] = self.feed
        return context

    def get_queryset(self):
        blacklist_users = self.request.user.blacklist

        queryset = (
            self.feed.messages
            .exclude(username__in=blacklist_users)
            .select_related('source', 'duplicate')
            .prefetch_related(
                'duplicate__messages',
                'duplicate__messages__source',
                'files'
            )
            .order_by("-date", 'id')
            .annotate(
                favorites=models.Case(
                    models.When(users_favorites__pk=self.request.user.pk,
                                then=models.Value(True)),
                    default=models.Value(False),
                    output_field=models.BooleanField(),
                )
            )
        )
        return queryset

    def list(self, request, *args, **kwargs):
        result = super().list(request, *args, **kwargs)
        self.feed.last_retrieve = now()
        self.feed.new_messages = 0
        self.feed.save()
        return result


class FavoritesMessageList(MessageList):
    def get_queryset(self):
        queryset = (
            self.request.user.favorites
            .select_related()
            .prefetch_related(
                'duplicate__messages',
                'duplicate__messages__source',
                'files'
            )
            .annotate(
                favorites=models.Case(
                    models.When(users_favorites__pk=self.request.user.pk,
                                then=models.Value(True)),
                    default=models.Value(False),
                    output_field=models.BooleanField(),
                ),
            ).order_by("-date", 'id')
        )
        return queryset


class FailOverMessageList(MessageList):
    permission_classes = [IsSubscribedPermission]

    def get_queryset(self):
        feeds = Feed.objects.filter(
            models.Q(user=self.request.user) |
            models.Q(users=self.request.user)
        ).values_list('id', flat=True)
        queryset = super().get_queryset().exclude(
            feedmessage__feed_id__in=feeds
        ).prefetch_related(
            'duplicate__messages',
            'duplicate__messages__source',
            'files'
        )
        return queryset
