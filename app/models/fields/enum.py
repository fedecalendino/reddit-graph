import typing

from django.db import models

if typing.TYPE_CHECKING:
    from app.models.base import BaseEnum


class EnumField(models.CharField):
    def __init__(self, enum: "BaseEnum", *args, **kwargs):
        self.enum = enum

        kwargs.setdefault("default", None)
        kwargs["choices"] = self.enum.choices()

        super().__init__(*args, **kwargs)

    def deconstruct(self):  # pragma: no cover
        name, path, args, kwargs = super().deconstruct()
        del kwargs["choices"]
        return name, path, [self.enum] + args, kwargs
