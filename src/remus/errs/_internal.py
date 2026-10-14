from dataclasses import dataclass
from typing import final


@final
@dataclass(frozen=True, slots=True)
class IndexErr:
    index: int

    def __str__(self) -> str:  # pragma: no cover
        return f"index out of range: {self.index}"


@final
@dataclass(frozen=True, slots=True)
class KeyErr[K]:
    key: K

    def __str__(self) -> str:  # pragma: no cover
        return f"key not found: {self.key}"


@final
@dataclass(frozen=True, slots=True)
class ValueErr[T]:
    value: T
    reason: str

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.reason}: {self.value}"
