from app.models.base import BaseEnum


class SubredditType(BaseEnum):
    ARCHIVED = "archived"
    BANNED = "banned"
    DELETED = "deleted"
    EMPLOYEES = "employees"
    PREMIUM = "premium"
    PRIVATE = "private"
    PUBLIC = "public"
    RESTRICTED = "restricted"
    USER = "user"
    NON_EXISTENT = "non-existent"
    ERROR = "error"


SUBREDDIT_TYPES = {
    "archived": SubredditType.ARCHIVED,
    "employees_only": SubredditType.EMPLOYEES,
    "gold_only": SubredditType.PREMIUM,
    "private": SubredditType.PRIVATE,
    "public": SubredditType.PUBLIC,
    "restricted": SubredditType.RESTRICTED,
    "user": SubredditType.USER,
}
