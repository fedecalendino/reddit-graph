import logging

from django.db import models

from app.models.base import BaseModel

logger = logging.getLogger(__name__)


class Subreddit(BaseModel):
    class Meta:
        db_table = "subreddits"

    name = models.CharField(
        max_length=100,
        primary_key=True,
        unique=True,
    )

    subscribers = models.IntegerField()
    type = models.TextField()

    def __str__(self):
        return f"{self.name}"
