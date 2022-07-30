import logging

from django.db import models

from src.models.base import BaseModel

logger = logging.getLogger(__name__)


class Queue(BaseModel):
    class Meta:
        db_table = "queue"

    name = models.CharField(
        max_length=100,
        primary_key=True,
        unique=True,
    )

    def __str__(self):
        return f"queue: {self.name}"
