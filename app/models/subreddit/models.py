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
    subscribers = models.IntegerField()
    type = fields.EnumField(
        SubredditType,
        default=SubredditType.PUBLIC,
        max_length=SubredditType.max_length(),
    )

    def __str__(self):
        return f"{self.name}"
