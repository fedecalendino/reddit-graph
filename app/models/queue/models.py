import logging

from django.db import models

from app.models.base import BaseModel

logger = logging.getLogger(__name__)


class Queue(BaseModel):
    class Meta:
        db_table = "queue"

    # Fields
    name = models.CharField(
        max_length=25,
        primary_key=True,
        unique=True,
    )

    priority = models.IntegerField(
        default=0,
    )

    # Methods
    def __str__(self):
        return f"{self.name}"
