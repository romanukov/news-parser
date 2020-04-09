from rest_framework import generics, views, mixins
from telegram_watcher.models.feed import Feed
from telegram_watcher.serializers import FeedSerializer, FeedDetailSerializer
from django.db import models


__all__ = [
    "FeedList",
    "FeedDetail"
]


class FeedList(mixins.CreateModelMixin,
               generics.ListAPIView):
    def get_serializer_class(self):
        if self.request.method == "GET":
            return FeedSerializer
        else:
            return FeedDetailSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_queryset(self):
        return (
            Feed.objects.filter(
                models.Q(user=self.request.user) |
                models.Q(users=self.request.user)
            )
        )


class FeedDetail(mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 mixins.RetrieveModelMixin,
                 generics.GenericAPIView):
    serializer_class = FeedDetailSerializer

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def perform_destroy(self, instance: Feed):
        if instance.user != self.request.user:
            instance.users.remove(self.request.user)
            return
        return super().perform_destroy(instance)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def get_queryset(self):
        return (
            Feed.objects.filter(
                models.Q(user=self.request.user) |
                models.Q(users=self.request.user)
            )
            .filter(pk=self.kwargs.get("pk"))
            .prefetch_related("sources")
        )

