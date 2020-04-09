from django.db import models
from .user import User


__all__ = ["Subscription"]


class Subscription(models.Model):
    stripe_token = models.CharField(max_length=4096)
    till = models.DateTimeField()
    created = models.DateTimeField(auto_created=True, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriptions"
    )
