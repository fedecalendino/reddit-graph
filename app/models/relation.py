import logging

from django.db import models

from .base import BaseModel
from .subreddit import Subreddit

logger = logging.getLogger(__name__)


class Relation(BaseModel):
    class Meta:
        db_table = "relations"

    type = models.CharField(
        max_length=100,
    )

    source = models.ForeignKey(
        Subreddit,
        on_delete=models.DO_NOTHING,
    )
    target = models.ForeignKey(
        Subreddit,
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return f"{self.source} > {self.target}"
