import logging
import re
from typing import Dict, Iterable, Tuple

from django.conf import settings
from django.utils import timezone

from app.constants import CURRENT_LINK_VERSION, EXCLUDED
from app import helpers
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

    excluded = EXCLUDED | {praw_subreddit.display_name.lower()}

    links = {
        LinkType.DESCRIPTION: _get_description_links(praw_subreddit),
        LinkType.SIDEBAR: _get_sidebar_links(praw_subreddit),
        LinkType.TOPBAR: _get_topbar_links(praw_subreddit),
        LinkType.WIKI: _get_wiki_links(praw_subreddit, limit=settings.WIKI_PAGES_LIMIT),
    }

    logger.info("    * fetching linked subreddits")

    for link_type, linked_subreddits in links.items():
        new_links = []
        updated_links = []

        # logger.info("    * fetching %s linked subreddits", link_type)

        try:
            filtered_linked_subreddits = sorted(
                filter(
                    lambda name: name not in excluded and validate_subreddit_name(name),
                    set(linked_subreddits),
                )
            )

            for linked_subreddit_name in filtered_linked_subreddits:
                try:
                    link, created = _get_model(
                        praw_subreddit=praw_subreddit,
                        linked_subreddit_name=linked_subreddit_name,
                        link_type=link_type,
                    )

                    if created:
                        new_links.append(link)
                    else:
                        updated_links.append(link)
                except Exception as exc:
                    pass
                    # logger.error(
                    #     "      - error with %s > [%s] > %s: %s",
                    #     subreddit.name,
                    #     link_type,
                    #     linked_subreddit_name,
                    #     str(exc),
                    # )

        except Exception as exc:
            pass
            # logger.info(
            #     "      - error fetching %s linked subreddits: %s",
            #     link_type,
            #     str(exc),
            # )

        _save_links(new_links, updated_links, link_type)

    return links


def _save_links(new_links, updated_links, link_type: LinkType):
    # logger.info(
    #     "    * saving %s %s links",
    #     link_type,
    #     len(new_links) + len(updated_links),
    # )

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


def _get_model(
    praw_subreddit,
    linked_subreddit_name: str,
    link_type: LinkType,
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
    yield from helpers.find_links(
        text=praw_subreddit.public_description,
    )


def _get_sidebar_links(praw_subreddit) -> Iterable[str]:
    try:
        # check config/sidebar for old subreddits that didn't add related subreddits
        sidebar_wiki = praw_subreddit.wiki["config/sidebar"]
        yield from helpers.find_links(
            text=sidebar_wiki.content_html,
        )
    except:
        pass

    # check sidebar widgets for related subreddits.
    for widget_name in praw_subreddit.widgets.layout["sidebar"]["order"]:
        widget = praw_subreddit.widgets.items.get(widget_name)

        if not widget:
            continue

        if widget.kind == "textarea":
            yield from helpers.find_links(
                text=widget.text,
            )

        if widget.kind == "community-list":
            yield from map(
                lambda value: value.display_name.lower(),
                widget.data,
            )


def _get_topbar_links(praw_subreddit) -> Iterable[str]:
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
            yield from helpers.find_links(
                text=item.url,
            )


def _get_wiki_links(praw_subreddit, limit: int = 250) -> Iterable[str]:
    index = 0
    errors = 0

    iterator = iter(praw_subreddit.wiki)

    while index < limit:
        if errors == 3:
            break

        try:
            wikipage = next(iterator)

            if wikipage.name.startswith("config"):
                # logger.info("      > %s. %s (skipped)", index, wikipage.name)
                continue

            # logger.info("      > %s. %s", index, wikipage.name)

            yield from helpers.find_links(
                text=wikipage.content_html,
            )

            index += 1
            errors = 0
        except Exception as exc:
            errors += 1
            # logger.debug("      > %s. %s (error)", index, str(exc))
