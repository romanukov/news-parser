from rest_framework import generics, mixins, views
from telegram_watcher.serializers import SourceSerializer, SourceListSerializer, SourceGroupSerializer
from telegram_watcher.models import UserSource, SourceGroup
from django.core.exceptions import ValidationError


__all__ = [
    "SourceList",
    "SourceGroupList",
    "SourceDetail"
]


class SourceGroupList(generics.ListAPIView):
    serializer_class = SourceGroupSerializer
    queryset = SourceGroup.objects.all()


class SourceList(mixins.CreateModelMixin,
                 generics.ListAPIView):
    def get_serializer_class(self):
        if self.request.method == "GET":
            return SourceListSerializer
        else:
            return SourceSerializer

    def post(self, request, *args, **kwargs):
        try:
            return self.create(request, *args, **kwargs)
        except ValidationError:
            return views.Response({"non_field_errors": ["This source already exists"]}, status=400)

    def get_queryset(self):
        return self.request.user.sources.all().order_by("-id")


class SourceDetail(mixins.UpdateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   generics.GenericAPIView):
    serializer_class = SourceSerializer

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        return UserSource.objects.filter(user=self.request.user, source=instance).delete()

    def get_queryset(self):
        return self.request.user.sources.all()

