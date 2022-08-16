import logging

from django.conf import settings

from app import actions
from app.models import Queue
from app.models.subreddit import Subreddit

logger = logging.getLogger(__name__)


def run():
    counter = 0
    subreddits_only = settings.SUBREDDITS_ONLY

    while True:
        current = Queue.objects.order_by("-priority", "name").first()
        counter += 1

        if current:
            logger.info("%d. fetching queued %s", counter, current.name)
            subreddit: Subreddit = actions.get_subreddit(current.name)
        else:
            logger.info("%d. fetching random subreddit", counter)
            subreddit: Subreddit = actions.get_random_subreddit(counter % 4 == 0)
            subreddits_only = False

        if subreddit:
            logger.info("%d. >>> saved: %s", counter, subreddit)

            if not subreddits_only:
                actions.get_relations(subreddit)
                actions.update_queue(subreddit)

        if current:
            current.delete()
