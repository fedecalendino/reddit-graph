import logging
from datetime import datetime

import pytz
from django.utils import timezone
from prawcore.exceptions import Forbidden

from app.constants import CURRENT_SUBREDDIT_VERSION
from app.models.subreddit import Subreddit, SubredditType, SUBREDDIT_TYPES
from app.reddit import reddit
from .helpers import is_valid_subreddit_name

logger = logging.getLogger(__name__)


def get_random_name(nsfw: bool = False) -> str:
    subreddit = reddit.random_subreddit(nsfw=nsfw)
    name = subreddit.display_name.lower()

    logger.debug(
        "fetched random subreddit: /r/%s",
        " (nsfw)" if nsfw else "",
        name,
    )

    return name


def get(name: str) -> Subreddit:
    if not is_valid_subreddit_name(name):
        return None

    subreddits = list(reddit.info(subreddits=[name.lower()]))

    if not subreddits:
        model = _get_model(name)
        model.type = SubredditType.NON_EXISTENT
        return model

    try:
        return _process_data(subreddits[0])
    except Exception as exc:
        model = _get_model(name)
        model.type = SubredditType.ERROR
        model.description = str(exc)
        return model


def _get_model(name: str) -> Subreddit:
    try:
        model = Subreddit.objects.get(
            name=name.lower(),
        )
    except Subreddit.DoesNotExist:
        model = Subreddit(
            name=name.lower(),
        )

    model.created_at = None
    model.updated_at = timezone.now()
    model.version = CURRENT_SUBREDDIT_VERSION

    return model


def _process_data(subreddit) -> Subreddit:
    model = _get_model(subreddit.display_name)

    model.id = subreddit.id
    model.description = subreddit.public_description
    model.type = SUBREDDIT_TYPES.get(subreddit.subreddit_type)
    model.title = subreddit.title
    model.created_at = datetime.utcfromtimestamp(subreddit.created_utc).replace(
        tzinfo=pytz.UTC
    )

    if model.type == SubredditType.PUBLIC:
        try:
            subreddit.quarantine
        except Forbidden as exc:
            subreddit.quaran.opt_in()

        model.color = subreddit.key_color
        model.img_banner = subreddit.banner_background_image
        model.img_header = subreddit.header_img
        model.img_icon = subreddit.icon_img
        model.nsfw = subreddit.over18
        model.quarantined = subreddit.quarantine
        model.subscribers = subreddit.subscribers

    model.save()

    return model
