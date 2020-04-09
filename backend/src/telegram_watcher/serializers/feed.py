from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from telegram_watcher.models import Feed, FeedSource, Source, SourceGroup

__all__ = ["FeedSerializer", "FeedDetailSerializer"]


class FeedSerializer(serializers.ModelSerializer):
    pre_defined = serializers.BooleanField(read_only=True)

    class Meta:
        model = Feed
        fields = (
            'name',
            'words',
            'id',
            'last_retrieve',
            'new_messages',
            'pre_defined'
        )


class FeedSourceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Source
        fields = ('link', 'type', 'id')
        validators = []


class SourceGroupSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = SourceGroup
        fields = ('id', 'name')
        validators = []


class FeedDetailSerializer(serializers.ModelSerializer):
    last_retrieve = serializers.DateTimeField(read_only=True)
    id = serializers.IntegerField(read_only=True)
    sources = FeedSourceSerializer(many=True)
    source_groups = SourceGroupSerializer(many=True)
    words = serializers.CharField(allow_blank=True)
    name = serializers.CharField()
    pre_defined = serializers.BooleanField(read_only=True)

    def create(self, validated_data):
        sources = validated_data.pop("sources", [])
        source_groups = validated_data.pop("source_groups", [])
        obj = Feed.objects.create(
            **validated_data,
            user=self.context["request"].user
        )
        for s in source_groups:
            source_group = SourceGroup.objects.get(pk=s["id"])
            obj.source_groups.add(source_group)
        obj.save()
        for s in sources:
            fs = FeedSource(feed=obj, source_id=s["id"])
            try:
                fs.validate_unique()
            except ValidationError:
                continue
            fs.save()
        return obj

    def update(self, instance, validated_data):
        if instance.pre_defined:
            return instance
        sources = validated_data.pop("sources", [])

        source_groups = validated_data.pop("source_groups", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.source_groups.clear()
        instance.feedsource_set.all().delete()
        for s in source_groups:
            source_group = SourceGroup.objects.get(pk=s["id"])
            instance.source_groups.add(source_group)
        instance.save()

        _sources = Source.objects.filter(
            pk__in=[s["id"] for s in sources]
        ).exclude(
            source_groups__id__in=[s["id"] for s in source_groups]
        )

        for source in _sources:
            fs = FeedSource(
                feed=self.instance,
                source=source
            )
            try:
                fs.validate_unique()
            except ValidationError:
                continue
            try:
                fs.save()
            except IntegrityError:
                continue
        return instance

    class Meta:
        model = Feed
        fields = (
            'name',
            'words',
            'id',
            'last_retrieve',
            'new_messages',
            'sources',
            'source_groups',
            'new_sources',
            'new_messages',
            'pre_defined'
        )
