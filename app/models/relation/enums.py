from app.models.base import BaseEnum


class RelationType(BaseEnum):
    DESCRIPTION = "description"
    SIDEBAR = "sidebar"
    TOPBAR = "topbar"
    WIKI = "wiki"
