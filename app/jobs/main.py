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
            logger.info("%d. fetched %s", number, subreddit)

        if current:
            current.delete()


def fetch_subreddit_random(nsfw: bool = False) -> Subreddit:
    logger.debug("fetching random subreddit (nsfw = %s)", nsfw)
    return fetch_subreddit("random" if not nsfw else "randnsfw")


def is_valid_subreddit_name(name: str, extra_exclusions: Set[str] = None) -> bool:
    if len(name) > 25:
        return False

    if not re.findall(SUBREDDIT_REGEX, f"/r/{name.lower()}", flags=re.IGNORECASE):
        return False

    if name in EXCLUDED:
        return False

    if name in (extra_exclusions or set()):
        return False

    return True


def fetch_subreddit(name: str) -> Subreddit:
    if not is_valid_subreddit_name(name):
        return None

    name = name.lower()

    try:
        sub = reddit.subreddit(name)

        try:
            sub.quarantine
        except Forbidden as exc:
            sub.quaran.opt_in()

        return _process_public_subreddit(sub)
    except Forbidden as exc:
        type_ = SubredditType.PRIVATE
    except NotFound as exc:
        type_ = SubredditType.BANNED
    except Redirect as exc:
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
    subreddit.description = sub.public_description
    subreddit.img_banner = sub.banner_background_image
    subreddit.img_header = sub.header_img
    subreddit.img_icon = sub.icon_img
    subreddit.nsfw = sub.over18
    subreddit.quarantined = sub.quarantine
    subreddit.subscribers = sub.subscribers
    subreddit.title = sub.title
    subreddit.type = SubredditType.PUBLIC
    subreddit.updated_at = timezone.now()
    subreddit.version = 3

    subreddit.save()

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

    subreddit.type = type_
    subreddit.updated_at = timezone.now()
    subreddit.version = 3

    subreddit.save()

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
        new_relations = []
        updated_relations = []

        logger.debug("    * fetching %s related subreddits", relation_type)

        for related_subreddit in sorted(set(related_subreddits)):
            if not is_valid_subreddit_name(related_subreddit):
                continue

            try:
                try:
                    relation = Relation.objects.get(
                        source=subreddit.name,
                        target=related_subreddit,
                        type=relation_type,
                    )
                    updated_relations.append(relation)
                    # logger.info("      - updating %s", relation)
                except Relation.DoesNotExist:
                    relation = Relation(
                        source=subreddit.name,
                        target=related_subreddit,
                        type=relation_type,
                    )
                    new_relations.append(relation)
                    # logger.info("      - adding %s", relation)

                relation.updated_at = timezone.now()
                relation.version = 1
            except Exception as exc:
                logger.error(
                    "      - error with %s > [%s] > %s: %s",
                    subreddit.name,
                    relation_type,
                    related_subreddit,
                    str(exc),
                )

        logger.debug(
            "    * saving %s %s relations",
            relation_type,
            len(new_relations) + len(updated_relations),
        )

        if new_relations:
            Relation.objects.bulk_create(
                new_relations,
                batch_size=250,
            )
            logger.debug(
                "    * created %s new %s relations",
                len(new_relations),
                relation_type,
            )

        if updated_relations:
            Relation.objects.bulk_update(
                updated_relations,
                batch_size=250,
                fields=["updated_at", "version"],
            )
            logger.debug(
                "    * updated %s %s relations",
                len(updated_relations),
                relation_type,
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
    index = 0
    errors = 0

    iterator = iter(sub.wiki)

    while index < limit:
        try:
            if errors == 3:
                break

            wikipage = next(iterator)

            if wikipage.name.startswith("config"):
                logger.debug("      > %s. %s (skipped)", index, wikipage.name)
                continue

            logger.debug("      > %s. %s", index, wikipage.name)

            yield from filter(
                lambda name: name not in excluded,
                re.findall(
                    SUBREDDIT_REGEX,
                    str(wikipage.content_html).lower(),
                    flags=re.IGNORECASE,
                ),
            )

            index += 1
            errors = 0
        except Exception as exc:
            errors += 1
            logger.debug("      > %s. %s (error)", index, str(exc))


def _update_queue(subreddit: Subreddit):
    targets = set(
        Relation.objects.filter(source=subreddit.name)
        .exclude(
            target__in=(
                Subreddit.objects.filter(
                    updated_at__gt=timezone.now() - timedelta(days=14)
                )
                .values("name")
                .all()
            )
        )
        .exclude(target__in=Queue.objects.values("name").all())
        .order_by("target")
        .values_list("target", flat=True)
        .all()
    )

    items = []

    for target in targets:
        items.append(Queue(name=target))

    if not items:
        return

    logger.debug("    + queuing %s names", len(items))
    Queue.objects.bulk_create(items, batch_size=250)
    logger.info("    + queued %s names", len(items))
