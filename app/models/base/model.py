from django.db import models


class BaseModel(models.Model):
    class Meta:
        abstract = True

    # Fields
    created_at = models.DateTimeField(
        blank=True,
        default=None,
        editable=False,
        null=True,
    )

    updated_at = models.DateTimeField(
        blank=True,
        default=None,
        editable=False,
        null=True,
    )
