from app.models.base import BaseEnum


class SubredditType(BaseEnum):
    PUBLIC = "public"
    PRIVATE = "private"
    BANNED = "banned"
    USER = "user"
    NON_EXISTENT = "non-existent"
    ERROR = "error"


SUBREDDIT_TYPES = {
    "public": SubredditType.PUBLIC,
    "private": SubredditType.PRIVATE,
    "banned": SubredditType.BANNED,
    "restricted": SubredditType.BANNED,
    "user": SubredditType.USER,
    "error": SubredditType.ERROR,
}
