from django.db.models import Q
from rest_framework import serializers, generics, views, exceptions
from telegram_watcher.models.message import Message
from ...permissions import IsSubscribedPermission
from ...serializers import MessageSerializer
from rest_framework.permissions import AllowAny



__all__ = [
    "AddMessageToFavorites",
    "RemoveMessageFromFavorites",
    "AddAuthorToBlacklist",
    "RemoveAuthorFromBlacklist",
    "SharedMessageView",
    "ShareMessageActionView",
]


class SharedMessageView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Message.objects.filter(shared=True)


class ShareMessageActionView(views.APIView):
    permission_classes = [IsSubscribedPermission]
    def get(self, *args, pk=None):
        if pk is None or self.request.user is None:
            raise exceptions.MethodNotAllowed
        # TODO: fix source checking

        Message.objects.filter(
            pk=pk
            # (Q(source__account=self.request.user) |
            #  Q(feed_set__user=self.request.user))
        ).update(shared=True)
        return views.Response({"success": True})


class AddMessageToFavorites(views.APIView):
    permission_classes = [IsSubscribedPermission]
    def get(self, *args, pk=None):
        if pk is None or self.request.user is None:
            return views.Response({"success": False})
        # TODO: fix source checking
        msg = Message.objects.filter(
            # source__in=self.request.user.sources.all(),
            pk=pk
        ).get()
        self.request.user.favorites.add(msg)
        return views.Response({"success": True})


class RemoveMessageFromFavorites(views.APIView):
    def get(self, *args, pk=None):
        if pk is None or self.request.user is None:
            return views.Response({"success": False})
        # TODO: fix source checking
        msg = Message.objects.filter(
            # source__in=self.request.user.sources.all(),
            pk=pk
        ).get()
        self.request.user.favorites.remove(msg)
        return views.Response({"success": True})


class AddAuthorToBlacklist(views.APIView):
    def get(self, *args, pk=None):
        if pk is None or self.request.user is None:
            return views.Response({"success": False})
        # TODO: fix source checking
        msg = Message.objects.filter(
            # source__in=self.request.user.sources.all(),
            pk=pk
        ).get()
        self.request.user.add_to_blacklist(msg.username)
        self.request.user.save()
        return views.Response({"success": True})


class RemoveAuthorFromBlacklist(views.APIView):
    def get(self, *args, pk=None):
        if pk is None or self.request.user is None:
            return views.Response({"success": False})
        # TODO: fix source checking
        msg = Message.objects.filter(
            # source__in=self.request.user.sources.all(),
            pk=pk
        ).get()
        self.request.user.remove_from_blacklist(msg.username)
        self.request.user.save()
        return views.Response({"success": True})
