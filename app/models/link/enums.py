from app.models.base import BaseEnum


class LinkType(BaseEnum):
    DESCRIPTION = "description"
    SIDEBAR = "sidebar"
    TOPBAR = "topbar"
    WIKI = "wiki"
