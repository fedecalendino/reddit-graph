import logging

from django.db import models

from app.models import fields
from .enums import SubredditType

logger = logging.getLogger(__name__)


class Subreddit(models.Model):
    class Meta:
        db_table = "subreddits"

    # Fields
    name = models.CharField(
        max_length=25,
        primary_key=True,
        unique=True,
    )

    color = models.CharField(
        blank=True,
        default=None,
        max_length=7,
        null=True,
    )

    created_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    icon_url = models.URLField(
        blank=True,
        default=None,
        null=True,
    )

    id = models.CharField(
        blank=True,
        max_length=100,
        null=True,
    )

    last_update = models.DateTimeField(
        blank=True,
        null=True,
    )

    nsfw = models.BooleanField(
        blank=True,
        default=False,
        null=True,
    )

    quarantined = models.BooleanField(
        blank=True,
        default=False,
        null=True,
    )

    subscribers = models.IntegerField(
        default=-1,
    )

    title = models.TextField(
        blank=True,
        null=True,
    )

    type = fields.EnumField(
        SubredditType,
        default=SubredditType.PUBLIC,
        max_length=SubredditType.max_length(),
    )

    version = models.IntegerField(
        default=0,
    )

    # Properties
    @property
    def url(self) -> str:
        return f"https://reddit.com/r/{self.name}"

    # Methods
    def __str__(self) -> str:
        return f"{self.name}"
