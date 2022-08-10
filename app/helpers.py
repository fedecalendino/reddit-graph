import re
from typing import Set

from app.constants import EXCLUDED, SUBREDDIT_REGEX


def find_subreddits(text: str) -> Set[str]:
    return set(re.findall(SUBREDDIT_REGEX, text, flags=re.IGNORECASE))


def validate_subreddit_name(name: str) -> bool:
    if 1 < len(name) > 21:
        return False

    if not find_subreddits(f"/r/{name.lower()}"):
        return False

    if name in EXCLUDED:
        return False

    return True
