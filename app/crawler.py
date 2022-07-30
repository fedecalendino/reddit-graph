import logging
import re
from datetime import datetime
from typing import Iterable

import pytz
from django.utils import timezone
from prawcore.exceptions import NotFound, Forbidden, Redirect

from app.models.subreddit import Subreddit, SubredditType
from app.reddit import reddit

logger = logging.getLogger(__name__)

SUBREDDIT_REGEX = r"""/r/(\w*).*"""

EXCLUDED = {
    "all",
    "random",
    "randnsfw",
}


def fetch_random_subreddit(nsfw: bool = False) -> Subreddit:
    return fetch_subreddit("random" if not nsfw else "randnsfw")


def fetch_subreddit(name: str) -> Subreddit:
    sub = None
    name = name.lower()

    try:
        sub = reddit.subreddit(name)

        if sub.quarantine:
            sub.quaran.opt_in()

        name = sub.display_name.lower()
        type_ = SubredditType.PUBLIC
    except Forbidden:
        type_ = SubredditType.PRIVATE
    except NotFound:
        type_ = SubredditType.BANNED
    except Redirect:
        type_ = SubredditType.NON_EXISTENT
    except Exception as exc:
        logger.error(exc)
        type_ = SubredditType.ERROR

    subreddit, created = Subreddit.objects.get_or_create(name=name)
    subreddit.type = type_

    if type_ == SubredditType.PUBLIC:
        subreddit.id = sub.id
        subreddit.color = sub.key_color
        subreddit.icon_url = sub.icon_img
        subreddit.nsfw = sub.over18
        subreddit.quarantined = sub.quarantine
        subreddit.subscribers = sub.subscribers
        subreddit.title = sub.title
        subreddit.created_at = datetime.utcfromtimestamp(sub.created_utc).replace(
            tzinfo=pytz.UTC
        )

    subreddit.last_update = timezone.now()

    subreddit.save()

    return subreddit


def fetch_topbar_relations(subreddit: Subreddit) -> Iterable[str]:
    widgets = reddit.subreddit(subreddit.name).widgets

    found = set()

    for widget in widgets.topbar:
        if widget.kind != "menu":
            continue

        items = []

        for data in widget.data:
            if hasattr(data, "children"):
                items.extend(data.children)
            else:
                items.append(data)

        for item in items:
            found.update(
                set(
                    map(
                        lambda match: match.lower(),
                        re.findall(
                            SUBREDDIT_REGEX,
                            str(item.url),
                            flags=re.IGNORECASE,
                        ),
                    )
                )
            )

    yield from found - {subreddit.name} - EXCLUDED


def fetch_sidebar_relations(subreddit: Subreddit) -> Iterable[str]:
    widgets = reddit.subreddit(subreddit.name).widgets

    found = set()

    for widget in widgets.sidebar:
        if widget.kind != "community-list":
            continue

        found.update(
            set(
                map(
                    lambda value: value.display_name.lower(),
                    widget.data,
                )
            )
        )

    yield from found - {subreddit.name} - EXCLUDED


def fetch_wiki_relations(subreddit: Subreddit) -> Iterable[str]:
    try:
        wiki = reddit.subreddit(subreddit.name).wiki

        found = set()

        for index, wikipage in enumerate(wiki):
            found.update(
                set(
                    map(
                        lambda match: match.lower(),
                        re.findall(
                            SUBREDDIT_REGEX,
                            str(wikipage.content_html),
                            flags=re.IGNORECASE,
                        ),
                    )
                )
            )

        yield from found - {subreddit.name} - EXCLUDED
    except Forbidden:
        return
