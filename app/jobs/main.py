import logging
import os
import time

from django.conf import settings
from django.utils import timezone

from app import actions
from app.models.error import Error
from app.models.queue import Queue
from app.models.subreddit import Subreddit

MAKE_RELEASE = int(os.getenv("MAKE_RELEASE", "250000"))
ADD_POPULAR = int(os.getenv("POPULAR", "100000"))
ADD_OUTDATED = int(os.getenv("ADD_OUTDATED", "2500"))
ANALYZE_RANDOM = int(os.getenv("ANALYZE_RANDOM", "50"))

logger = logging.getLogger(__name__)


def run():
    counter = 0
    subreddits_only = settings.SUBREDDITS_ONLY

    while True:
        name = None

        try:
            if counter % MAKE_RELEASE == 0:
                actions.make_release()

            if counter % ADD_POPULAR == 0:
                actions.fill_queue_with_popular_subreddits()

            if counter % ADD_OUTDATED == 0:
                actions.fill_queue_with_outdated_subreddits()

            if counter % ANALYZE_RANDOM != 0:
                current = Queue.objects.order_by("-priority", "name").first()
            else:
                current = None

            counter += 1

            if current:
                name = current.name
                logger.info(
                    "%d. fetching: /r/%s (p = %s)",
                    counter,
                    current.name,
                    current.priority,
                )
                subreddit: Subreddit = actions.get_subreddit(current.name)
            else:
                name = "random" if counter % 10 else "randnsfw"
                logger.info("%d. fetching: %s subreddit", counter, name)
                subreddit: Subreddit = actions.get_random_subreddit(counter % 10 == 0)
                subreddits_only = False

            if subreddit:
                name = subreddit.name
                logger.info("%d. >>> saved: %s", counter, subreddit)

                if not subreddits_only:
                    actions.get_links(subreddit)
                    actions.fill_queue_with_linked_subreddits(subreddit)

            if current:
                current.delete()
        except Exception as exc:
            logger.error(exc)

            Error(
                created_at=timezone.now(),
                updated_at=timezone.now(),
                name=name,
                description=exc,
            ).save()

            time.sleep(60)
