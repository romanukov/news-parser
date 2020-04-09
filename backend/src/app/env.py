from os import environ
from envparse import Env

__all__ = ['env']

env = Env(
    DEBUG=bool,
    SECRET_KEY=str,

    DB_DATABASE=dict(cast=str, default="tg_parser"),
    DB_USER=dict(cast=str, default="tg_parser"),
    DB_PASSWORD=dict(cast=str, default="tg_parser"),
    DB_HOST=dict(cast=str, default=environ.get('DOCKER_HOST_IP')),
    DB_PORT=dict(cast=str, default='5432'),

    TELEGRAM_API_ID=int,
    TELEGRAM_API_HASH=str,

    TWITTER_ACCESS_TOKEN=str,
    TWITTER_ACCESS_TOKEN_SECRET=str,
    TWITTER_CONSUMER_KEY=str,
    TWITTER_CONSUMER_SECRET=str,

    RSS_CHECK_PERIOD=int,
    REDIS_PORT=dict(cast=int, default=6379),
    REDIS_HOST=dict(cast=str, default="redis"),
    ALLOWED_HOSTS=dict(cast=list, subcast=str),
    DEFAULT_STORE_DAYS=dict(cast=int, default=28),
    STRIPE_SECRET=str,
    STRIPE_PLAN=str,
    STRIPE_PUBLIC=str,
    STRIPE_PRODUCT=str,
    SENDGRID_API_KEY=str,

    EMAIL_HOST=str,
    EMAIL_PORT=int,
    EMAIL_HOST_USER=str,
    EMAIL_HOST_PASSWORD=str,
    EMAIL_USE_TLS=bool,
    EMAIL_USE_SSL=bool,
    EMAIL_FROM=str,
    SENTRY_DSN=str,
    DJANGO_LOG_LEVEL=dict(cast=str, default='WARNING'),
    TELEGRAM_SYNC_SOURCES=dict(cast=bool, default=True),
    RUN_TWITTER_WORKER=dict(cast=bool, default=True),
    RUN_TELEGRAM_WORKER=dict(cast=bool, default=True),
    RUN_RSS_WORKER=dict(cast=bool, default=True),

    AMQP_HOST=dict(cast=str),
)
