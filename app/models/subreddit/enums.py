from app.models.base import BaseEnum


class SubredditType(BaseEnum):
    ARCHIVED = "archived"
    BANNED = "banned"
    DELETED = "deleted"
    EMPLOYEES_ONLY = "employees-only"
    GOLD_ONLY = "gold-only"
    PRIVATE = "private"
    PUBLIC = "public"
    RESTRICTED = "restricted"
    USER = "user"
    NON_EXISTENT = "non-existent"
    ERROR = "error"


SUBREDDIT_TYPES = {
    "archived": SubredditType.ARCHIVED,
    "employees_only": SubredditType.EMPLOYEES_ONLY,
    "gold_only": SubredditType.GOLD_ONLY,
    "private": SubredditType.PRIVATE,
    "public": SubredditType.PUBLIC,
    "restricted": SubredditType.RESTRICTED,
    "user": SubredditType.USER,
}
