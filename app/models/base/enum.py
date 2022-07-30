from enum import Enum
from typing import Tuple, List


class BaseEnum(str, Enum):
    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        return [(item.value, item.name) for item in cls]

    @classmethod
    def max_length(cls) -> int:
        return max(map(len, cls))

    # Dunders
    def __str__(self) -> str:  # pragma: no cover
        return str(self.value)
