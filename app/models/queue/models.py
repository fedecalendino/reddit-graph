import logging

from app.models.base import BaseModel

logger = logging.getLogger(__name__)


class Queue(BaseModel):
    class Meta:
        db_table = "queue"

    def __str__(self):
        return f"queue: {self.id}"
