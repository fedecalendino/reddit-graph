import logging

from django.db import models

from app.models import fields
from app.models.base import BaseModel
from .enums import SubredditType

logger = logging.getLogger(__name__)


class Subreddit(BaseModel):
    class Meta:
        db_table = "subreddits"

    # Fields
    name = models.CharField(
        max_length=100,
        primary_key=True,
        unique=True,
    )

    color = models.CharField(
        blank=True,
        default=None,
        max_length=7,
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

    nsfw = models.BooleanField(
        default=False,
    )

    quarantined = models.BooleanField(
        default=False,
    )

    subscribers = models.IntegerField(
        default=0,
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

    # Properties
    @property
    def url(self):
        return f"https://reddit.com/r/{self.name}"

    # Methods
    def __str__(self):
        return f"{self.name}"
