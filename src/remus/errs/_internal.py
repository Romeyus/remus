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
class ValueErr[T]:
    value: T
    context: str

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.context}: {self.value}"
