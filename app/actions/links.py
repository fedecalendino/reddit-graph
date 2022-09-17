import logging
import re
from typing import Dict, Iterable, Tuple

from django.conf import settings
from django.utils import timezone

from app.constants import (
    EXCLUDED,
    SUBREDDIT_REGEX,
    CURRENT_LINK_VERSION,
)
from app.helpers import validate_subreddit_name
from app.models.link import Link, LinkType
from app.models.subreddit import Subreddit
from app.reddit import reddit

logger = logging.getLogger(__name__)


def get(subreddit: Subreddit) -> Dict[LinkType, Link]:
    praw_subreddits = list(reddit.info(subreddits=[subreddit.name.lower()]))

    if not praw_subreddits:
        return

    praw_subreddit = praw_subreddits[0]

    links = {
        LinkType.DESCRIPTION: _get_description_links(
            praw_subreddit,
        ),
        LinkType.SIDEBAR: _get_sidebar_links(
            praw_subreddit,
        ),
        LinkType.TOPBAR: _get_topbar_links(
            praw_subreddit,
        ),
        LinkType.WIKI: _get_wiki_links(
            praw_subreddit,
            limit=settings.WIKI_PAGES_LIMIT,
        ),
    }

    for link_type, linked_subreddits in links.items():
        new_links = []
        updated_links = []

        logger.info("    * fetching %s linked subreddits", link_type)

        try:
            for linked_subreddit in sorted(set(linked_subreddits)):
                if not validate_subreddit_name(linked_subreddit):
                    continue

                try:
                    link, created = _get_model(
                        praw_subreddit, linked_subreddit, link_type
                    )

                    if created:
                        new_links.append(link)
                    else:
                        updated_links.append(link)
                except Exception as exc:
                    logger.error(
                        "      - error with %s > [%s] > %s: %s",
                        subreddit.name,
                        link_type,
                        linked_subreddit,
                        str(exc),
                    )
        except Exception as exc:
            logger.info(
                "      - error fetching %s linked subreddits: %s",
                link_type,
                str(exc),
            )

        logger.info(
            "    * saving %s %s links",
            link_type,
            len(new_links) + len(updated_links),
        )

        if new_links:
            Link.objects.bulk_create(
                new_links,
                batch_size=250,
            )
            logger.info(
                "      + created %s new %s links",
                len(new_links),
                link_type,
            )

        if updated_links:
            Link.objects.bulk_update(
                updated_links,
                batch_size=250,
                fields=["updated_at", "version"],
            )
            logger.info(
                "      + updated %s %s links",
                len(updated_links),
                link_type,
            )

    return links


def _get_model(
    praw_subreddit, linked_subreddit_name: str, link_type: LinkType
) -> Tuple[Link, bool]:
    try:
        created = False
        link = Link.objects.get(
            source=praw_subreddit.display_name.lower(),
            target=linked_subreddit_name,
            type=link_type,
        )
    except Link.DoesNotExist:
        created = True
        link = Link(
            source=praw_subreddit.display_name.lower(),
            target=linked_subreddit_name,
            type=link_type,
        )
        link.created_at = timezone.now()

    link.version = CURRENT_LINK_VERSION
    link.updated_at = timezone.now()

    return link, created


def _get_description_links(praw_subreddit) -> Iterable[str]:
    subreddit_name = praw_subreddit.display_name.lower()

    yield from filter(
        lambda name: name not in EXCLUDED | {subreddit_name},
        re.findall(
            SUBREDDIT_REGEX,
            str(praw_subreddit.public_description.lower()),
            flags=re.IGNORECASE,
        ),
    )


def _get_sidebar_links(praw_subreddit) -> Iterable[str]:
    subreddit_name = praw_subreddit.display_name.lower()

    items = set()

    try:
        # check config/sidebar wiki page for old subreddits that didn't add related links
        sidebar_wiki = praw_subreddit.wiki["config/sidebar"]

        items.update(
            re.findall(
                SUBREDDIT_REGEX,
                str(sidebar_wiki.content_html.lower()),
                flags=re.IGNORECASE,
            )
        )
    except:
        pass

    for widget_name in praw_subreddit.widgets.layout["sidebar"]["order"]:
        widget = praw_subreddit.widgets.items.get(widget_name)

        if not widget or widget.kind != "community-list":
            continue

        items.update(
            map(
                lambda value: value.display_name.lower(),
                widget.data,
            )
        )

    yield from filter(
        lambda name: name not in EXCLUDED | {subreddit_name},
        items,
    )


def _get_topbar_links(praw_subreddit) -> Iterable[str]:
    subreddit_name = praw_subreddit.display_name.lower()

    for widget_name in praw_subreddit.widgets.layout["topbar"]["order"]:
        widget = praw_subreddit.widgets.items.get(widget_name)

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
                lambda name: name not in EXCLUDED | {subreddit_name},
                re.findall(
                    SUBREDDIT_REGEX,
                    str(item.url.lower()),
                    flags=re.IGNORECASE,
                ),
            )


def _get_wiki_links(praw_subreddit, limit: int = 250) -> Iterable[str]:
    subreddit_name = praw_subreddit.display_name.lower()

    index = 0
    errors = 0

    iterator = iter(praw_subreddit.wiki)

    while index < limit:
        if errors == 3:
            break

        try:
            wikipage = next(iterator)

            if wikipage.name.startswith("config"):
                logger.info("      > %s. %s (skipped)", index, wikipage.name)
                continue

            logger.info("      > %s. %s", index, wikipage.name)

            yield from filter(
                lambda name: name not in EXCLUDED | {subreddit_name},
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
