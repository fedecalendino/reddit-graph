import logging

from app.reddit import reddit

logger = logging.getLogger(__name__)


def random_subreddit_name(nsfw: bool = False) -> str:
    subreddit = reddit.random_subreddit(nsfw=nsfw)

    logger.debug(
        "fetched random subreddit: /r/%s",
        " (nsfw)" if nsfw else "",
        subreddit.display_name.lower(),
    )

    return subreddit.display_name.lower()
