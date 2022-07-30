import logging

from django.db import models

from app.models import fields
from app.models.base import BaseModel
from app.models.subreddit import Subreddit
from .enums import RelationType

logger = logging.getLogger(__name__)


class Relation(BaseModel):
    class Meta:
        db_table = "relations"

    # Fields
    type = fields.EnumField(
        RelationType,
        max_length=RelationType.max_length(),
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
