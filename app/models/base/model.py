from django.db import models


class BaseModel(models.Model):
    class Meta:
        abstract = True

    id = models.CharField(
        max_length=100,
        primary_key=True,
        unique=True,
    )

    # Fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        blank=True,
        editable=False,
        null=True,
    )
