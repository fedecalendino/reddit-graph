import logging
import time

from django.conf import settings
from django.utils import timezone

from app import actions
from app.models.error import Error
from app.models.queue import Queue
from app.models.subreddit import Subreddit

logger = logging.getLogger(__name__)


def run():
    counter = 0
    subreddits_only = settings.SUBREDDITS_ONLY

    while True:
        name = None

        try:
            current = Queue.objects.order_by("-priority", "name").first()
            counter += 1

            if current:
                name = current.name
                logger.info("%d. fetching queued %s", counter, current.name)
                subreddit: Subreddit = actions.get_subreddit(current.name)
            else:
                name = "random" if counter % 10 else "randnsfw"
                logger.info("%d. fetching random subreddit", counter)
                subreddit: Subreddit = actions.get_random_subreddit(counter % 10 == 0)
                subreddits_only = False

            if subreddit:
                name = subreddit.name
                logger.info("%d. >>> saved: %s", counter, subreddit)

                if not subreddits_only:
                    actions.get_relations(subreddit)
                    actions.update_queue(subreddit)

            if current:
                current.delete()
        except Exception as exc:
            logger.error(exc)
            Error(
                created_at=timezone.now(),
                updated_at=timezone.now(),
                name=name,
                description=exc
            ).save()
            time.sleep(60)
