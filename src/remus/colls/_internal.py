from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator, MutableSequence, Sequence
from dataclasses import dataclass
from typing import final, override

from remus._internal import Err, Maybe, Ok, Result, panic


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

    def get_or_else(self, index: int, default_factory: Callable[[], T]) -> T:
        return self.get(index).unwrap_or_else(default_factory)

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


class BaseMutArray[T](BaseArray[T], ABC):
    def append(self, value: T) -> None:
        self.insert(len(self), value)

    @abstractmethod
    def insert(self, index: int, value: T) -> None: ...

    @abstractmethod
    def __delitem__(self, index: int) -> None: ...

    @abstractmethod
    def __setitem__(self, index: int, value: T) -> None: ...


@dataclass(frozen=True, slots=True)
class MutArray[T](Array[T], BaseMutArray[T]):
    data: MutableSequence[T]

    @override
    def insert(self, index: int, value: T) -> None:
        self.data.insert(index, value)

    @override
    def __delitem__(self, index: int) -> None:
        try:
            del self.data[index]

        except IndexError:
            panic(str(IndexErr(index)))

    @override
    def __setitem__(self, index: int, value: T) -> None:
        try:
            self.data[index] = value

        except IndexError:
            panic(str(IndexErr(index)))


@final
@dataclass(frozen=True, slots=True)
class IndexErr:
    index: int

    def __str__(self) -> str:  # pragma: no cover
        return f"index out of range: {self.index}"
