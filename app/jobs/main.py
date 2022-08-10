import logging

from app import actions
from app.models import Queue
from app.models.subreddit import Subreddit

logger = logging.getLogger(__name__)


def run():
    counter = 0

    while True:
        current = Queue.objects.order_by("-priority", "name").first()
        counter += 1

        if current:
            logger.info("%d. fetching %s (queue)", counter, current.name)
            subreddit: Subreddit = actions.get_subreddit(current.name)
        else:
            logger.info("%d. fetching random subreddit", counter)
            subreddit: Subreddit = actions.get_random_subreddit(counter % 4 == 0)

        if subreddit:
            logger.info("%d. fetched %s", counter, subreddit)

            actions.get_relations(subreddit)
            actions.update_queue(subreddit)

        if current:
            current.delete()
