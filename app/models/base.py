from django.db import models


class BaseModel(models.Model):
    class Meta:
        abstract = True

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
