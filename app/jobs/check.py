from app import fetch
from app.models import Relation, Queue, Subreddit
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def run(name):
    subreddit = fetch.subreddit(name)

    for relation_type, related_subreddits in fetch.relations(subreddit).items():
        for related_subreddit in related_subreddits:
            relation, created = Relation.objects.get_or_create(
                source=subreddit.name,
                target=related_subreddit,
                type=relation_type,
            )

            relation.last_update = timezone.now()
            relation.save()

            logger.info("Saved %s", relation)
