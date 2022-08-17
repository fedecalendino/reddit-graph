import logging
import uuid

from django.db import models

from app.models.base import BaseModel

logger = logging.getLogger(__name__)


class Error(BaseModel):
    class Meta:
        db_table = "errors"

    # Fields
    id = models.CharField(
        default=uuid.uuid4,
        max_length=36,
        primary_key=True,
    )

    name = models.CharField(
        blank=True,
        default=None,
        max_length=25,
        null=True,
    )

    description = models.TextField()

    # Methods
    def __str__(self):
        return f"{self.name}"
