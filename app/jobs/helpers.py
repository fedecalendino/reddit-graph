import logging
import re
from datetime import datetime, timedelta
from typing import Dict, Iterable, Set

import pytz
from django.utils import timezone
from prawcore.exceptions import Forbidden
from prawcore.exceptions import NotFound, Redirect

from app.constants import EXCLUDED, DAYS_TO_UPDATE, SUBREDDIT_REGEX
from app.models import Queue
from app.models.relation import Relation, RelationType
from app.models.subreddit import Subreddit, SubredditType
from app.reddit import reddit


def find_subreddits(text: str):
    return re.findall(SUBREDDIT_REGEX, text, flags=re.IGNORECASE)


def is_valid_subreddit_name(name: str) -> bool:
    if 1 < len(name) > 21:
        return False

    if not find_subreddits(f"/r/{name.lower()}"):
        return False

    if name in EXCLUDED:
        return False

    return True
