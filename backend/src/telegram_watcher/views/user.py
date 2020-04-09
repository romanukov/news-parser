from rest_framework import generics, mixins, views, exceptions
from telegram_watcher.serializers import UserSerializer
from telegram_watcher.models import User
from rest_framework.permissions import AllowAny


__all__ = [
    "ProfileDetail",
    "CheckEmailView"
]


class ProfileDetail(mixins.UpdateModelMixin,
                    mixins.RetrieveModelMixin,
                    generics.GenericAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class CheckEmailView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if email is None:
            raise exceptions.ValidationError()
        if User.objects.filter(username=email).exists():
            return views.Response({
                "exists": True
            })
        return views.Response({
            "exists": False
        })
