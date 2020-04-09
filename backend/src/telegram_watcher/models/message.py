from django.db import models, connection
import tsvector_field
from django.contrib.postgres.fields import JSONField

import re

from telegram_watcher.models import Source
from storages.backends.sftpstorage import SFTPStorage
from django.contrib.postgres.indexes import BrinIndex, GistIndex


__all__ = ("Message", "DuplicateIndex", "MessageFile")


class DuplicateIndex(models.Model):
    """
    This table contains pk only.
    """
    pass


class CDNFileStorage(SFTPStorage):
    def url(self, name):
        return f'https://user27211.clients-cdnnow.ru/{name}'


class MessageFile(models.Model):
    file = models.FileField(storage=CDNFileStorage())
    message = models.ForeignKey("Message", on_delete=models.CASCADE, related_name='files')

    class Meta:
        indexes = [
            models.Index(fields=['message']),
        ]


class Message(models.Model):
    text = models.TextField(
        null=True
    )
    search = tsvector_field.SearchVectorField([
        tsvector_field.WeightedColumn('text', 'A'),
    ], 'simple')
    source = models.ForeignKey(
        Source,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    username = models.CharField(
        max_length=254,
        null=True,
        blank=True
    )
    created = models.DateTimeField(
        auto_created=True,
        auto_now_add=True,
        blank=True
    )  # date of create record
    meta = JSONField(blank=True, null=True)
    date = models.DateTimeField(db_index=True)  # date of create message
    duplicate = models.ForeignKey(DuplicateIndex, models.SET_NULL,
                                  null=True, related_name="messages")
    internal_id = models.BigIntegerField(null=True)
    shared = models.BooleanField(default=False)

    def _recount_dublicates(self):
        duplicates = self._get_duplicates()
        for dupe in duplicates:
            if dupe.duplicate is None:
                self.duplicate = DuplicateIndex.objects.create()
            else:
                self.duplicate = dupe.duplicate
            if dupe.duplicate is not None and self.duplicate_id != dupe.duplicate_id:
                dupe.duplicate.delete()
            dupe.duplicate = self.duplicate
            dupe.save()
        self.save()

    def _get_duplicates(self):
        # Find duplicates for new messages
        q = str(self.text)
        q = re.sub(r"(https?:[\S]+)|(<[^>]*>)", " ", q)  # Remove urls and html tags
        q = re.sub(r"[^\w\s\-\.\/]+", " ", q)  # Remove all specials symblos

        # Fulltext search Query
        duplicates = Message.objects.exclude(pk=self.pk).extra(
            where=[
                "telegram_watcher_message.search @@ plainto_tsquery('simple', %s)"
            ],
            params=[q],
        )

        duplicates_list = list(filter(
            lambda d: d.text == self.text,
            duplicates
        ))
        return duplicates_list

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.created:
            return super().save(force_insert, force_update, using, update_fields)
        duplicates = self._get_duplicates()
        for dupe in duplicates:
            if self.duplicate is None:
                self.duplicate = dupe.duplicate or DuplicateIndex.objects.create()
            if dupe.duplicate is not None and self.duplicate_id != dupe.duplicate_id:
                dupe.duplicate.delete()
            dupe.duplicate = self.duplicate
            dupe.save()
        return super().save(force_insert, force_update, using, update_fields)

    @classmethod
    def fulltext_search(cls, search: str, pre_queryset=None):
        """

        :param search: query
        :param pre_queryset: queryset for filter
        :return:
        """
        query = search
        queryset = cls.objects
        if pre_queryset is not None:
            queryset = pre_queryset
        res = queryset.extra(
            where=[
                "telegram_watcher_message.search @@ to_tsquery('simple', %s)"
            ],
            params=[query],
        )
        return res

    def __str__(self):
        return self.text or "None"

    class Meta:
        indexes = [
            models.Index(fields=['-date']),
            # models.Index(fields=['source']),
            # BrinIndex(fields=['date', 'id', 'source']),
        ]
