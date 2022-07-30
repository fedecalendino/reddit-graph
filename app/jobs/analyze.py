import logging

from time import sleep

from app import fetch
from app.models import Relation, Queue, Subreddit

logger = logging.getLogger(__name__)


def normal(name: str):
    sleep(0.25)

    logger.info("Analyzing %s", name)

    subreddit = fetch.subreddit(name)
    _update_queue(subreddit)


def random(nsfw: bool = False):
    sleep(0.25)

    logger.info("Analyzing random subreddit (nsfw = %s)", nsfw)

    subreddit = fetch.random(nsfw)
    _update_queue(subreddit)


def _update_queue(subreddit: Subreddit):
    for relation in Relation.objects.filter(source=subreddit.name).all():
        if not Subreddit.objects.filter(name=relation.target).first():
            Queue.objects.get_or_create(name=relation.target)
            logger.info("Queue %s", relation.target)
