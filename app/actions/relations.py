import logging
import re
from typing import Dict, Iterable, Tuple

from django.utils import timezone

from app.constants import (
    EXCLUDED,
    SUBREDDIT_REGEX,
    CURRENT_RELATION_VERSION,
)
from app.helpers import validate_subreddit_name
from app.models.relation import Relation, RelationType
from app.models.subreddit import Subreddit, SubredditType
from app.reddit import reddit

logger = logging.getLogger(__name__)


def get(subreddit: Subreddit) -> Dict[RelationType, Relation]:
    if subreddit.type != SubredditType.PUBLIC:
        return {}

    praw_subreddit = reddit.subreddit(subreddit.name)

    relations = {
        RelationType.SIDEBAR: _get_sidebar_relations(praw_subreddit),
        RelationType.TOPBAR: _get_topbar_relations(praw_subreddit),
        RelationType.WIKI: _get_wiki_relations(praw_subreddit),
    }

    for relation_type, related_subreddits in relations.items():
        new_relations = []
        updated_relations = []

        logger.debug("    * fetching %s related subreddits", relation_type)

        for related_subreddit in sorted(set(related_subreddits)):
            if not validate_subreddit_name(related_subreddit):
                continue

            try:
                relation, created = _get_model(
                    praw_subreddit, related_subreddit, relation_type
                )

                if created:
                    new_relations.append(relation)
                else:
                    updated_relations.append(relation)
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


def _get_model(
    subreddit: Subreddit, related_subreddit_name: str, relation_type: RelationType
) -> Tuple[Relation, bool]:
    try:
        created = False
        relation = Relation.objects.get(
            source=subreddit.name,
            target=related_subreddit_name,
            type=relation_type,
        )
    except Relation.DoesNotExist:
        created = True
        relation = Relation(
            source=subreddit.name,
            target=related_subreddit_name,
            type=relation_type,
        )

    relation.version = CURRENT_RELATION_VERSION
    relation.updated_at = timezone.now()

    return relation, created


def _get_sidebar_relations(praw_subreddit) -> Iterable[str]:
    for widget in praw_subreddit.widgets.sidebar:
        if widget.kind != "community-list":
            continue

        yield from filter(
            lambda name: name not in EXCLUDED | {praw_subreddit.display_name.lower()},
            map(
                lambda value: value.display_name.lower(),
                widget.data,
            ),
        )


def _get_topbar_relations(praw_subreddit) -> Iterable[str]:
    for widget in praw_subreddit.widgets.topbar:
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
                lambda name: name
                not in EXCLUDED | {praw_subreddit.display_name.lower()},
                re.findall(
                    SUBREDDIT_REGEX,
                    str(item.url.lower()),
                    flags=re.IGNORECASE,
                ),
            )


def _get_wiki_relations(praw_subreddit, limit: int = 250) -> Iterable[str]:
    index = 0
    errors = 0

    iterator = iter(praw_subreddit.wiki)

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
                lambda name: name
                not in EXCLUDED | {praw_subreddit.display_name.lower()},
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
