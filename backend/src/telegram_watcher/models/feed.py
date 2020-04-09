import re

from django.db import models

from .source import Source
from .message import Message
from .user import User
from .mixins import ModelDiffMixin


__all__ = ("Feed", "FeedMessage", "FeedSource")


class FeedSource(models.Model):
    """
    Trough ManyToMany relation model Feed to Source
    """
    feed = models.ForeignKey(
        'Feed',
        on_delete=models.CASCADE
    )  # FK to Feed
    source = models.ForeignKey(
        Source,
        on_delete=models.CASCADE
    )  # FK to Source
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = (('feed', 'source'),)


class FeedMessage(models.Model):
    """
    Trough ManyToMany relation model Message to Feed
    """
    feed = models.ForeignKey(
        'Feed',
        on_delete=models.CASCADE
    )  # FK to Feed
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE
    )  # FK to Message
    feed_source = models.ForeignKey(
        FeedSource,
        on_delete=models.CASCADE
    )  # Key for delete all FeedMessage models after deleting FeedSource (after delete source too)
    date = models.DateTimeField(
        auto_now_add=True
    )  # Date of created relation

    class Meta:
        unique_together = (('feed', 'message'),)
        indexes = [
            models.Index(fields=['feed']),
            models.Index(fields=['message']),
        ]


class Feed(ModelDiffMixin, models.Model):
    name = models.CharField(
        max_length=254
    )
    words = models.TextField(blank=True)
    last_retrieve = models.DateTimeField(
        null=True
    )
    messages = models.ManyToManyField(
        Message,
        blank=True,
        through=FeedMessage
    )
    new_sources = models.BooleanField(
        default=False
    )
    new_messages = models.IntegerField(default=0)
    sources = models.ManyToManyField(
        Source,
        through=FeedSource,
        related_name="feeds"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="feeds",
        null=True,
        blank=True
    )
    pre_defined = models.BooleanField(default=False)
    users = models.ManyToManyField(
        User,
        related_name="m2m_feeds",
        blank=True
    )
    source_groups = models.ManyToManyField(
        "SourceGroup",
        related_name="feeds",
        blank=True
    )

    @staticmethod
    def _process_lexem(lex):
        # Lex in quotes
        if re.match(r'^"[^\"]+"$', lex):
            return lex.replace(r' ', "<->").replace(r'\"', "")
        # Lex not in quotes
        return "%s:*" % lex

    @staticmethod
    def process_expression(query):
        """

        :param query:
        :return:
        """
        lexems = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', query)
        q = " & ".join([
            Feed._process_lexem(lex)
            for lex in lexems
        ])

        return q

    @property
    def fulltext_query(self):
        """
        Converts the user's search string into something suitable for passing to
        to_tsquery.
        """
        query = ""
        if self.words:
            query = "|".join([
                self.process_expression(s)
                for s in self.words.split("\r\n")
            ])

        return query

    def messages_queryset(self):
        return Message.fulltext_search(
            self.fulltext_query,
            Message.objects.filter(source__in=self.sources.all())
        )

    def __str__(self):
        return self.name
