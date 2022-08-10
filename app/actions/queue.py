import logging
from datetime import timedelta

from django.utils import timezone

from app.constants import DAYS_TO_UPDATE
from app.models import Queue, Relation, Subreddit

logger = logging.getLogger(__name__)


def update(subreddit: Subreddit):
    targets = set(
        Relation.objects.filter(source=subreddit.name)
        .exclude(
            target__in=(
                Subreddit.objects.filter(
                    updated_at__gt=timezone.now() - timedelta(days=DAYS_TO_UPDATE)
                )
                .values("name")
                .all()
            )
        )
        .exclude(target__in=Queue.objects.values("name").all())
        .order_by("target")
        .values_list("target", flat=True)
        .all()
    )

    items = []

    for target in targets:
        items.append(Queue(name=target))

    if not items:
        return

    logger.info("    + queuing %s names", len(items))
    Queue.objects.bulk_create(items, batch_size=250)
    logger.info("    + queued %s names", len(items))
