from app.models.base import BaseEnum


class SubredditType(BaseEnum):
    PUBLIC = "public"
    PRIVATE = "private"
    BANNED = "banned"
    NON_EXISTENT = "non-existent"
    USER = "user"
    ERROR = "error"
