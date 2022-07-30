import logging
import re
from typing import Dict, Iterable, Set

from prawcore.exceptions import Forbidden

from app.constants import SUBREDDIT_REGEX, EXCLUDED
from app.models.relation import RelationType
from app.models.subreddit import Subreddit, SubredditType
from app.reddit import reddit

logger = logging.getLogger(__name__)


def fetch_relations(subreddit: Subreddit) -> Dict:
    if subreddit.type != SubredditType.PUBLIC:
        return {}

    sub = reddit.subreddit(subreddit.name)
    excluded = {sub.display_name.lower()} | EXCLUDED

    return {
        RelationType.SIDEBAR: set(_fetch_sidebar_relations(sub, excluded)),
        RelationType.TOPBAR: set(_fetch_topbar_relations(sub, excluded)),
        RelationType.WIKI: set(_fetch_wiki_relations(sub, excluded)),
    }


def _fetch_sidebar_relations(sub, excluded: Set[str]) -> Iterable[str]:
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


def _fetch_topbar_relations(sub, excluded: Set[str]) -> Iterable[str]:
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


def _fetch_wiki_relations(sub, excluded: Set[str]) -> Iterable[str]:
    try:
        for wikipage in sub.wiki:
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
