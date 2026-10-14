from collections.abc import (
    Callable,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)
from dataclasses import dataclass, field

from remus import Err, Maybe, Nothing, Ok, Result, Some, errs


# ==========================================
# ===            Arrays                 ===
# ==========================================
@dataclass(frozen=True, slots=True)
class Array[T]:
    data: Sequence[T] = field(default_factory=tuple[T])

    def count(self, value: T) -> int:
        return self.data.count(value)

    def first(self) -> Maybe[T]:
        return self.get(0)

    def get(self, index: int) -> Maybe[T]:
        try:
            return Some(self.data[index])
        except IndexError:
            return Nothing

    def get_or(self, index: int, default: T) -> T:
        return self.get(index).unwrap_or(default)

    def get_or_else(self, index: int, default_factory: Callable[[], T]) -> T:
        return self.get(index).unwrap_or_else(default_factory)

    def index(self, value: T) -> Maybe[int]:
        try:
            return Some(self.data.index(value))
        except ValueError:
            return Nothing

    def last(self) -> Maybe[T]:
        return self.get(-1)

    def __contains__(self, value: T) -> bool:
        return value in self.data

    def __iter__(self) -> Iterator[T]:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)


@dataclass(frozen=True, slots=True)
class MutArray[T](Array[T]):
    data: MutableSequence[T] = field(default_factory=list[T])

    def append(self, value: T) -> None:
        self.data.append(value)

    def clear(self) -> None:
        self.data.clear()

    def insert(self, index: int, value: T) -> None:
        self.data.insert(index, value)

    def pop(self, index: int) -> Result[T, errs.IndexErr]:
        try:
            return Ok(self.data.pop(index))
        except IndexError:
            return Err(errs.IndexErr(index))

    def pop_or(self, index: int, default: T) -> T:
        return self.pop(index).unwrap_or(default)

    def pop_or_else(self, index: int, default_factory: Callable[[], T]) -> T:
        return self.pop(index).ok().unwrap_or_else(default_factory)

    def prepend(self, value: T) -> None:
        self.insert(0, value)

    def remove(self, value: T) -> Result[None, errs.ValueErr[T]]:
        try:
            return Ok(self.data.remove(value))
        except ValueError:
            return Err(errs.ValueErr(value, "value not in array"))

    def set(self, index: int, value: T) -> Result[None, errs.IndexErr]:
        try:
            self.data[index] = value
            return Ok(None)
        except IndexError:
            return Err(errs.IndexErr(index))


# ==========================================
# ===            Maps                 ===
# ==========================================
@dataclass(frozen=True, slots=True)
class Map[K, T]:
    data: Mapping[K, T] = field(default_factory=dict[K, T])

    def items(self) -> Iterable[tuple[K, T]]:
        return self.data.items()

    def keys(self) -> Iterable[K]:
        return self.data.keys()

    def get(self, key: K) -> Maybe[T]:
        value = self.data.get(key)
        if value is None:
            return Nothing
        return Some(value)

    def get_or(self, key: K, default: T) -> T:
        return self.get(key).unwrap_or(default)

    def get_or_else(self, key: K, default_factory: Callable[[], T]) -> T:
        return self.get(key).unwrap_or_else(default_factory)

    def values(self) -> Iterable[T]:
        return self.data.values()

    def __contains__(self, key: K) -> bool:
        return key in self.data

    def __iter__(self) -> Iterator[K]:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)


@dataclass(frozen=True, slots=True)
class MutMap[K, T](Map[K, T]):
    data: MutableMapping[K, T] = field(default_factory=dict[K, T])

    def clear(self) -> None:
        self.data.clear()

    def pop(self, key: K) -> Result[T, errs.KeyErr[K]]:
        try:
            return Ok(self.data.pop(key))
        except KeyError:
            return Err(errs.KeyErr(key))

    def pop_or(self, key: K, default: T) -> T:
        return self.pop(key).unwrap_or(default)

    def pop_or_else(self, key: K, default_factory: Callable[[], T]) -> T:
        return self.pop(key).ok().unwrap_or_else(default_factory)

    def set(self, key: K, value: T) -> None:
        self.data[key] = value

    def set_default(self, key: K, default: T) -> T:
        return self.data.setdefault(key, default)
