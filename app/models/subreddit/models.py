import logging
from typing import List

from django.db import models

from app.models import base
from app.models import fields
from app.models.relation import Relation, RelationType
from .enums import SubredditType

logger = logging.getLogger(__name__)


class Subreddit(base.BaseModel):
    class Meta:
        db_table = "subreddits"

    # Fields
    name = models.CharField(
        max_length=25,
        primary_key=True,
        unique=True,
    )

    color = models.CharField(
        blank=True,
        default=None,
        max_length=7,
        null=True,
    )

    description = models.TextField(
        blank=True,
        default=None,
        null=True,
    )

    img_banner = models.URLField(
        blank=True,
        default=None,
        null=True,
    )

    img_header = models.URLField(
        blank=True,
        default=None,
        null=True,
    )

    img_icon = models.URLField(
        blank=True,
        default=None,
        null=True,
    )

    id = models.CharField(
        blank=True,
        max_length=100,
        null=True,
    )

    new = models.BooleanField(
        default=False,
    )

    nsfw = models.BooleanField(
        blank=True,
        default=None,
        null=True,
    )

    quarantined = models.BooleanField(
        blank=True,
        default=None,
        null=True,
    )

    subscribers = models.IntegerField(
        blank=True,
        default=None,
        null=True,
    )

    title = models.TextField(
        blank=True,
        null=True,
    )

    type = fields.EnumField(
        SubredditType,
        default=SubredditType.PUBLIC,
        max_length=SubredditType.max_length(),
    )

    version = models.IntegerField(
        default=0,
    )

    # Properties

    def relations(self, type: RelationType = None) -> List[Relation]:
        if not type:
            return list(Relation.objects.filter(source=self.name).all())

        return list(Relation.objects.filter(source=self.name, type=type).all())

    @property
    def sidebar_relations(self) -> List[Relation]:
        return self.relations(RelationType.SIDEBAR)

    @property
    def topbar_relations(self) -> List[Relation]:
        return self.relations(RelationType.TOPBAR)

    @property
    def wiki_relations(self) -> List[Relation]:
        return self.relations(RelationType.WIKI)

    @property
    def url(self) -> str:
        return f"https://reddit.com/r/{self.name}"

    # Methods
    def __str__(self) -> str:
        string = f"/r/{self.name} [{self.type}][subs={self.subscribers}]"

        if self.nsfw:
            string = f"{string}[nsfw]"

        if self.quarantined:
            string = f"{string}[quarantined]"

        return string
