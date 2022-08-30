import logging
from datetime import timedelta

from django.utils import timezone

from app.constants import DAYS_TO_UPDATE
from app.models import Queue, Relation, Subreddit
from app.reddit import reddit

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
        items.append(
            Queue(
                created_at=timezone.now(),
                updated_at=timezone.now(),
                name=target,
                priority=-1,
            )
        )

    if not items:
        return

    logger.info("    * queuing %s names", len(items))
    Queue.objects.bulk_create(items, batch_size=250)
    logger.info("      + queued %s names", len(items))


def fill():
    items = []

    logger.info("fetching popular subreddits")

    for sub in reddit.subreddits.popular(limit=1000):
        items.append(
            Queue(
                created_at=timezone.now(),
                updated_at=timezone.now(),
                name=sub.display_name.lower(),
                priority=-100,
            )
        )

    logger.info("  * queuing %s names", len(items))
    Queue.objects.bulk_create(items, batch_size=250)
    logger.info("    + queued %s names", len(items))
