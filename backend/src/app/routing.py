from django.conf.urls import url
from channels.auth import *
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter

from rest_framework_jwt.settings import api_settings
from telegram_watcher import consumers
from telegram_watcher.watcher import TelegramWatcher
from telegram_watcher.models import User


class JWTCookieAuthMiddleware:
    """
    Middleware which populates scope["user"] from a Django session.
    Requires SessionMiddleware to function.
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        # Make sure we have a session
        if "cookies" not in scope:
            raise ValueError(
                "AuthMiddleware cannot find cookies in scope. "
                "CookieMiddleware must be above it.")
        if "JWT-Cookie" not in scope["cookies"]:
            raise ValueError(
                "AuthMiddleware cannot find JWT-Cookie in cookies.")
        jwt_payload_handler = api_settings.JWT_DECODE_HANDLER
        jwt_payload = jwt_payload_handler(scope["cookies"]["JWT-Cookie"])
        user_id = jwt_payload.get("user_id")
        if user_id is None:
            raise ValueError("user_id not present in JWT payload.")
        # Add it to the scope if it's not there already
        if "user" not in scope:
            scope["user"] = User.objects.get(id=user_id)
        # Pass control to inner application
        return self.inner(scope)


application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': CookieMiddleware(JWTCookieAuthMiddleware(
        URLRouter([
            url('ws', consumers.notifier.NotifierConsumer)
        ])
    )),
    "telegram_watcher": None,
    "twitter_watcher": None
})
