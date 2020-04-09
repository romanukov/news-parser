from rest_framework import serializers

from telegram_watcher.models import Source, UserSource, SourceGroup


__all__ = ["SourceSerializer", "SourceListSerializer", "SourceGroupSerializer"]


class SourceListSerializer(serializers.ModelSerializer):
    msg_count = serializers.SerializerMethodField(read_only=True)
    active = serializers.BooleanField(read_only=True)

    def get_msg_count(self, instance):
        return getattr(instance, "msg_count", 0)

    class Meta:
        model = Source
        fields = ('link', 'type', 'id', 'msg_count', 'active', 'name')


class SourceGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceGroup
        fields = ('id', 'name')


class SourceSerializer(serializers.ModelSerializer):
    active = serializers.BooleanField(read_only=True)

    def create(self, validated_data):
        obj = UserSource(
            user=self.context["request"].user
        )

        if self.context["request"].user.is_staff:
            store_days = validated_data.get('store_days', 28)
        else:
            store_days = 28
        try:
            created, obj.source = False, Source.objects.get(
                type=validated_data['type'],
                link=validated_data['link'],
            )
        except Source.DoesNotExist:
            created, obj.source = True, Source.objects.create(
                type=validated_data['type'],
                link=validated_data['link'],
                language=validated_data['language'],
                store_days=store_days
            )
        if not created:
            if store_days is not None and (obj.source.store_days < store_days or store_days == 0):
                obj.source.store_days = store_days
                obj.source.save()
        obj.validate_unique()
        obj.save()
        return obj.source

    def update(self, instance, validated_data):
        if validated_data["link"] != instance.link or validated_data["type"] != instance.type:
            instance.delete()
            return super().create(validated_data)
        if instance.users.count() > 1:
            validated_data["store_days"] = validated_data.get('store_days')
        elif validated_data.get('store_days') < instance.store_days or validated_data.get('store_days') == 0:
            validated_data["store_days"] = instance.store_days
        return super().update(instance, validated_data)

    class Meta:
        model = Source
        fields = ('link', 'type', 'id', 'language', 'store_days', 'active', 'name')
        validators = []

