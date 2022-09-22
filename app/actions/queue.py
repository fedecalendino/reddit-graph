import logging
from datetime import timedelta

from django.utils import timezone

from app.constants import DAYS_TO_UPDATE, CURRENT_SUBREDDIT_VERSION
from app.models.queue import Queue
from app.models.link import Link
from app.models.subreddit import Subreddit, SubredditType
from app.reddit import reddit

logger = logging.getLogger(__name__)


def fill_with_linked_subreddits(subreddit: Subreddit):
    targets = set(
        Link.objects.filter(source=subreddit.name)
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
                priority=100_000_000 + (subreddit.subscribers if subreddit.subscribers else 0),
            )
        )

    if not items:
        return

    logger.info("    * queuing %s names", len(items))
    Queue.objects.bulk_create(items, batch_size=250)
    logger.info("      + queued %s names", len(items))


def fill_with_popular_subreddits():
    logger.info("fetching popular subreddits")

    items = []

    for sub in reddit.subreddits.popular(limit=1000):
        if sub.subscribers > 1_000_000:
            continue
        
        items.append(
            Queue(
                created_at=timezone.now(),
                updated_at=timezone.now(),
                name=sub.display_name.lower(),
                priority=-sub.subscribers,
            )
        )

    logger.info("  * queuing %s names", len(items))
    Queue.objects.bulk_create(items, batch_size=250)
    logger.info("    + queued %s names", len(items))


def fill_with_outdated_subreddits():
    logger.info("fetching popular subreddits")

    queryset = Subreddit.objects.filter(
        updated_at__lt=timezone.now() - timedelta(days=DAYS_TO_UPDATE),
    ).exclude(
        name__in=Queue.objects.values("name").all(),
    )

    excluded_types = [
        SubredditType.BANNED, 
        SubredditType.NON_EXISTENT,
        SubredditType.DELETED,
    ]

    items = []

    for subreddit in queryset.all():
        if subreddit.type in excluded_types:
            if subreddit.version == CURRENT_SUBREDDIT_VERSION:
                continue

        items.append(
            Queue(
                created_at=timezone.now(),
                updated_at=timezone.now(),
                name=subreddit.name.lower(),
                priority=subreddit.subscribers if subreddit.subscribers else 0,
            )
        )

    logger.info("  * queuing %s outdated subreddits", len(items))
    Queue.objects.bulk_create(items, batch_size=250)
    logger.info("    + queued %s outdated subreddits", len(items))
