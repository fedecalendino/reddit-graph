import logging
import uuid

from django.db import models

from .base import BaseModel
from .subreddit import Subreddit

logger = logging.getLogger(__name__)


class Relation(BaseModel):
    class Meta:
        db_table = "relations"

    # Fields
    type = models.CharField(
        max_length=100,
    )

    # Relations
    source = models.ForeignKey(
        Subreddit,
        related_name="sources",
        on_delete=models.DO_NOTHING,
    )

    target = models.ForeignKey(
        Subreddit,
        related_name="targets",
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return f"{self.source} > {self.target}"
