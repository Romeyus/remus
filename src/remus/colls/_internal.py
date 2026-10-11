from abc import ABC, abstractmethod
from collections.abc import Iterator, MutableSequence, Sequence
from dataclasses import dataclass
from typing import final, override

from remus._internal import Err, Maybe, Ok, Result


# ==========================================
# ===            Arrays                 ===
# ==========================================
class BaseArray[T](ABC):
    def count(self, value: T) -> int:
        hits = 0
        for i in self:
            if i == value:
                hits += 1
        return hits

    def get(self, index: int) -> Maybe[T]:
        return self[index].ok()

    def get_or(self, index: int, default: T) -> T:
        return self[index].unwrap_or(default)

    @abstractmethod
    def __contains__(self, value: T) -> bool: ...

    @abstractmethod
    def __getitem__(self, index: int) -> Result[T, IndexErr]: ...

    @abstractmethod
    def __iter__(self) -> Iterator[T]: ...

    @abstractmethod
    def __len__(self) -> int: ...


@dataclass(frozen=True, slots=True)
class Array[T](BaseArray[T]):
    data: Sequence[T]

    @override
    def __contains__(self, value: T) -> bool:
        return value in self.data

    @override
    def __getitem__(self, index: int) -> Result[T, IndexErr]:
        try:
            return Ok(self.data[index])

        except IndexError:
            return Err(IndexErr(index))

    @override
    def __iter__(self) -> Iterator[T]:
        return iter(self.data)

    @override
    def __len__(self) -> int:
        return len(self.data)


@dataclass(frozen=True, slots=True)
class MutArray[T](Array[T], BaseArray[T]):
    data: MutableSequence[T]


@final
@dataclass(frozen=True, slots=True)
class IndexErr:
    index: int

    def __str__(self) -> str:  # pragma: no cover
        return f"index out of range: {self.index}"
