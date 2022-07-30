import logging

from app.models import Queue
from . import analyze

logger = logging.getLogger(__name__)


def run():
    while True:
        current = Queue.objects.first()

        if not current:
            logger.info("Queue cleared")
            break

        logger.info("Next %s", current.name)

        analyze.normal(current.name)

        current.delete()
        logger.info("Dequeued %s", current.name)
