import logging
from datetime import datetime

import pytz
from django.utils import timezone
from prawcore.exceptions import NotFound, Forbidden, Redirect

from app.constants import EXCLUDED
from app.models.subreddit import Subreddit, SubredditType
from app.reddit import reddit

logger = logging.getLogger(__name__)


def fetch_random(nsfw: bool = False) -> Subreddit:
    return fetch_subreddit("random" if not nsfw else "randnsfw")


def fetch_subreddit(name: str) -> Subreddit:
    if name in EXCLUDED:
        return None

    name = name.lower()

    try:
        sub = reddit.subreddit(name)

        if sub.quarantine:
            sub.quaran.opt_in()

        return _process_public_subreddit(sub)
    except Forbidden:
        type_ = SubredditType.PRIVATE
    except NotFound:
        type_ = SubredditType.BANNED
    except Redirect:
        type_ = SubredditType.NON_EXISTENT
    except Exception as exc:
        logger.error(exc)
        type_ = SubredditType.ERROR

    return _create_non_public_subreddit(name, type_)


def _process_public_subreddit(sub) -> Subreddit:
    subreddit, created = Subreddit.objects.get_or_create(
        name=sub.display_name.lower(),
    )

    subreddit.id = sub.id
    subreddit.color = sub.key_color
    subreddit.created_at = datetime.utcfromtimestamp(sub.created_utc).replace(
        tzinfo=pytz.UTC
    )
    subreddit.icon_url = sub.icon_img
    subreddit.last_update = timezone.now()
    subreddit.nsfw = sub.over18
    subreddit.quarantined = sub.quarantine
    subreddit.subscribers = sub.subscribers
    subreddit.title = sub.title
    subreddit.type = SubredditType.PUBLIC

    subreddit.save()
    logger.info("Saved %s", subreddit.name)

    return subreddit


def _create_non_public_subreddit(name: str, type_: SubredditType) -> Subreddit:
    subreddit, created = Subreddit.objects.get_or_create(
        name=name,
    )

    subreddit.id = None
    subreddit.color = None
    subreddit.created_at = None
    subreddit.icon_url = None
    subreddit.last_update = timezone.now()
    subreddit.nsfw = None
    subreddit.quarantined = None
    subreddit.subscribers = -1
    subreddit.title = None
    subreddit.type = type_

    subreddit.save()

    return subreddit
