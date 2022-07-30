import logging

from django.db import models

from app.models.base import BaseModel

logger = logging.getLogger(__name__)


class Subreddit(BaseModel):
    class Meta:
        db_table = "subreddits"

    # Fields
    name = models.CharField(
        max_length=100,
        unique=True,
    )

    subscribers = models.IntegerField()

    type = models.TextField()

    def __str__(self):
        return f"{self.name}"
