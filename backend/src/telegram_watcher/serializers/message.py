from rest_framework import serializers
from django.db.models import Count
from .source import SourceSerializer
from telegram_watcher.models import Message, MessageFile
from django.utils.timezone import get_current_timezone


__all__ = ["MessageSerializer"]


class MessageFileSerializer(serializers.ModelSerializer):
    file = serializers.FileField(use_url=True)

    class Meta:
        model = MessageFile
        fields = ('file',)

class MessageSerializer(serializers.HyperlinkedModelSerializer):
    source = SourceSerializer(read_only=True)
    text = serializers.CharField()
    id = serializers.IntegerField()
    duplicate_id = serializers.IntegerField()
    blacklist = serializers.SerializerMethodField()
    favorites = serializers.SerializerMethodField()
    duplicates_sources_count = serializers.SerializerMethodField()
    duplicates_count = serializers.SerializerMethodField()
    new = serializers.SerializerMethodField()
    internal_id = serializers.CharField(allow_null=True)
    date = serializers.DateTimeField()
    files = MessageFileSerializer(many=True)
    meta = serializers.JSONField()

    def _duplicates_queryset(self, obj):
        return obj.duplicate.messages

    def get_duplicates_count(self, obj):
        if obj.duplicate_id is None:
            return 0
        return getattr(obj, "duplicates_count", self._duplicates_queryset(obj).count())

    def get_duplicates_sources_count(self, obj):
        if obj.duplicate_id is None:
            return 0
        source_ids = set()
        for msg in self._duplicates_queryset(obj).all():
            source_ids.add(msg.source_id)
        return len(source_ids)

    def get_blacklist(self, obj):
        if not hasattr(self.context["request"].user, 'blacklist'):
            return False
        if obj.username in self.context["request"].user.blacklist:
            return True
        else:
            return False

    def get_favorites(self, obj):
        return getattr(obj, "favorites", False)

    def get_new(self, obj):
        feed = self.context.get("feed")
        if feed is None:
            return False
        return feed.last_retrieve < obj.date if feed.last_retrieve is not None else True

    class Meta:
        model = Message
        fields = (
            'text',
            'id',
            'date',
            'source',
            'username',
            'blacklist',
            'favorites',
            'duplicate_id',
            'duplicates_sources_count',
            'duplicates_count',
            'new',
            'internal_id',
            'files',
            'meta'
        )
