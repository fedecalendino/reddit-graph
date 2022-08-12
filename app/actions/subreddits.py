import logging
from datetime import datetime
from typing import Tuple

import pytz
from django.utils import timezone
from prawcore.exceptions import Forbidden

from app.constants import CURRENT_SUBREDDIT_VERSION
from app.helpers import validate_subreddit_name
from app.models.subreddit import Subreddit, SubredditType, SUBREDDIT_TYPES
from app.reddit import reddit

logger = logging.getLogger(__name__)


def get_random(nsfw: bool = False) -> str:
    praw_subreddit = reddit.random_subreddit(nsfw=nsfw)
    name = praw_subreddit.display_name.lower()

    logger.debug(
        "fetched random %s subreddit: /r/%s",
        " (nsfw)" if nsfw else "",
        name,
    )

    return _process_data(praw_subreddit)


def get(name: str) -> Subreddit:
    if not validate_subreddit_name(name):
        return None

    subreddits = list(reddit.info(subreddits=[name.lower()]))

    if not subreddits:
        model, _ = _get_model(name)
        model.type = SubredditType.NON_EXISTENT
        model.save()
        return model

    try:
        return _process_data(subreddits[0])
    except Exception as exc:
        model, _ = _get_model(name)
        model.type = SubredditType.ERROR
        model.description = str(exc)
        model.save()
        return model


def _get_model(name: str) -> Tuple[Subreddit, bool]:
    try:
        created = False
        subreddit = Subreddit.objects.get(
            name=name.lower(),
        )
    except Subreddit.DoesNotExist:
        created = True
        subreddit = Subreddit(
            name=name.lower(),
        )

    subreddit.created_at = None
    subreddit.updated_at = timezone.now()
    subreddit.version = CURRENT_SUBREDDIT_VERSION

    return subreddit, created


def _process_data(praw_subreddit) -> Subreddit:
    subreddit, _ = _get_model(praw_subreddit.display_name)

    try:
        praw_subreddit.quarantine
    except Forbidden as exc:
        praw_subreddit.quaran.opt_in()

    subreddit.color = praw_subreddit.key_color
    subreddit.created_at = datetime.utcfromtimestamp(
        praw_subreddit.created_utc
    ).replace(tzinfo=pytz.UTC)
    subreddit.description = praw_subreddit.public_description
    subreddit.id = praw_subreddit.id
    subreddit.img_banner = praw_subreddit.banner_background_image
    subreddit.img_header = praw_subreddit.header_img
    subreddit.img_icon = praw_subreddit.icon_img
    subreddit.nsfw = praw_subreddit.over18
    subreddit.quarantined = praw_subreddit.quarantine
    subreddit.subscribers = praw_subreddit.subscribers
    subreddit.title = praw_subreddit.title
    subreddit.type = SUBREDDIT_TYPES.get(praw_subreddit.subreddit_type)

    if subreddit.type == SubredditType.PUBLIC:
        if subreddit.subscribers is None:
            subreddit.type = SubredditType.BANNED

    subreddit.save()

    return subreddit
