import logging
import re
from datetime import datetime, timedelta
from typing import Dict, Iterable, Set

import pytz
from django.utils import timezone
from prawcore.exceptions import Forbidden
from prawcore.exceptions import NotFound, Redirect

from app.constants import SUBREDDIT_REGEX, EXCLUDED
from app.models import Queue
from app.models.relation import Relation, RelationType
from app.models.subreddit import Subreddit, SubredditType
from app.reddit import reddit

logger = logging.getLogger(__name__)


def run():
    number = 0

    while True:
        number += 1
        current = Queue.objects.first()

        if current:
            logger.info("%d. fetching %s", number, current.name)
            subreddit = fetch_subreddit(current.name)
        else:
            nsfw = number % 4 == 0

            logger.info("%d. fetching %s", number, ("random", "randnsfw")[nsfw])
            subreddit = fetch_subreddit_random(nsfw)

        if subreddit:
            _update_queue(subreddit)

        logger.info(" -> dequeued %s \n\n", current.name)

        current.delete()


def fetch_subreddit_random(nsfw: bool = False) -> Subreddit:
    logger.info("fetching random subreddit (nsfw = %s)", nsfw)
    return fetch_subreddit("random" if not nsfw else "randnsfw")


def fetch_subreddit(name: str) -> Subreddit:
    if name in EXCLUDED:
        return None

    name = name.lower()

    logger.info("searching for subreddit /r/%s", name)

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

    return _process_non_public_subreddit(name, type_)


def _process_public_subreddit(sub) -> Subreddit:
    try:
        subreddit = Subreddit.objects.get(
            name=sub.display_name.lower(),
        )
    except Subreddit.DoesNotExist:
        subreddit = Subreddit(
            name=sub.display_name.lower(),
        )

    subreddit.id = sub.id
    subreddit.color = sub.key_color
    subreddit.created_at = datetime.utcfromtimestamp(sub.created_utc).replace(
        tzinfo=pytz.UTC
    )
    subreddit.description = sub.description
    subreddit.img_banner = sub.banner_background_image
    subreddit.img_header = sub.header_img
    subreddit.img_icon = sub.icon_img
    subreddit.last_update = timezone.now()
    subreddit.nsfw = sub.over18
    subreddit.quarantined = sub.quarantine
    subreddit.subscribers = sub.subscribers
    subreddit.title = sub.title
    subreddit.type = SubredditType.PUBLIC
    subreddit.version = 1

    subreddit.save()

    logger.info("saved %s", subreddit)

    fetch_relations(subreddit)

    return subreddit


def _process_non_public_subreddit(name: str, type_: SubredditType) -> Subreddit:
    try:
        subreddit = Subreddit.objects.get(
            name=name,
        )
    except Subreddit.DoesNotExist:
        subreddit = Subreddit(
            name=name,
        )

    subreddit.id = None
    subreddit.color = None
    subreddit.created_at = None
    subreddit.description = None
    subreddit.img_banner = None
    subreddit.img_header = None
    subreddit.img_icon = None
    subreddit.last_update = timezone.now()
    subreddit.nsfw = None
    subreddit.quarantined = None
    subreddit.subscribers = -1
    subreddit.title = None
    subreddit.type = type_
    subreddit.version = 1

    subreddit.save()

    logger.info("saved %s", subreddit)

    return subreddit


def fetch_relations(subreddit: Subreddit) -> Dict:
    if subreddit.type != SubredditType.PUBLIC:
        return {}

    sub = reddit.subreddit(subreddit.name)
    excluded = {sub.display_name.lower()} | EXCLUDED

    relations = {
        RelationType.SIDEBAR: _fetch_relations_sidebar(sub, excluded),
        RelationType.TOPBAR: _fetch_relations_topbar(sub, excluded),
        RelationType.WIKI: _fetch_relations_wiki(sub, excluded),
    }

    for relation_type, related_subreddits in relations.items():
        logger.info(" * fetching %s related subreddits", relation_type)

        for related_subreddit in sorted(set(related_subreddits)):
            try:
                try:
                    relation = Relation.objects.get(
                        source=subreddit.name,
                        target=related_subreddit,
                        type=relation_type,
                    )
                except Relation.DoesNotExist:
                    relation = Relation(
                        source=subreddit.name,
                        target=related_subreddit,
                        type=relation_type,
                    )

                relation.last_update = timezone.now()
                relation.version = 1
                relation.save()

                logger.info("saved %s", relation)
            except Exception as exc:
                logger.error(
                    "error with %s > [%s] > %s: %s",
                    subreddit.name,
                    relation_type,
                    related_subreddit,
                    str(exc),
                )

    return relations


def _fetch_relations_sidebar(sub, excluded: Set[str]) -> Iterable[str]:
    for widget in sub.widgets.sidebar:
        if widget.kind != "community-list":
            continue

        yield from filter(
            lambda name: name not in excluded,
            map(
                lambda value: value.display_name.lower(),
                widget.data,
            ),
        )


def _fetch_relations_topbar(sub, excluded: Set[str]) -> Iterable[str]:
    for widget in sub.widgets.topbar:
        if widget.kind != "menu":
            continue

        items = []

        for data in widget.data:
            if hasattr(data, "children"):
                items.extend(data.children)
            else:
                items.append(data)

        for item in items:
            yield from filter(
                lambda name: name not in excluded,
                re.findall(
                    SUBREDDIT_REGEX,
                    str(item.url.lower()),
                    flags=re.IGNORECASE,
                ),
            )


def _fetch_relations_wiki(sub, excluded: Set[str], limit: int = 250) -> Iterable[str]:
    try:
        for index, wikipage in enumerate(sub.wiki):
            if index == limit:
                break

            if wikipage.name.startswith("config"):
                logger.info("    %s. %s (skipped)", index, wikipage.name)
                continue

            logger.info("    %s. %s", index, wikipage.name)

            yield from filter(
                lambda name: name not in excluded,
                re.findall(
                    SUBREDDIT_REGEX,
                    str(wikipage.content_html).lower(),
                    flags=re.IGNORECASE,
                ),
            )
    except Forbidden:
        pass


def _update_queue(subreddit: Subreddit):
    now = timezone.now()
    threshold = now + timedelta(days=-5)

    for relation in (
        Relation.objects.filter(source=subreddit.name).order_by("target").all()
    ):
        try:
            related = Subreddit.objects.filter(name=relation.target).get()

            if related.last_update < threshold:
                queue = True
                message = "queued outdated subreddit %s"
            else:
                queue = False
                message = ""

        except Subreddit.DoesNotExist:
            queue = True
            message = "queued new subreddit %s"

        if queue:
            item, created = Queue.objects.get_or_create(name=relation.target)

            if created:
                logger.info(message, item)
