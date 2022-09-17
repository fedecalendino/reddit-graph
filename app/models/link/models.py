import logging
import uuid

from django.db import models

from app.models import fields
from app.models.base import BaseModel
from .enums import LinkType

logger = logging.getLogger(__name__)


class Link(BaseModel):
    class Meta:
        db_table = "links"
        constraints = [
            models.UniqueConstraint(
                name="id",
                fields=["source", "target", "type"],
            )
        ]

    id = models.CharField(
        default=uuid.uuid4,
        max_length=36,
        primary_key=True,
    )

    source = models.CharField(
        max_length=25,
    )

    target = models.CharField(
        max_length=25,
    )

    type = fields.EnumField(
        LinkType,
        max_length=LinkType.max_length(),
    )

    version = models.IntegerField(
        default=0,
    )

    # Methods
    def __str__(self):
        return f"{self.source} > [{self.type}] > {self.target}"
