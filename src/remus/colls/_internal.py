from collections.abc import (
    Callable,
    Iterable,
    Iterator,
    Mapping,
)
from typing import override

from remus import Err, Maybe, Nothing, Ok, Result, Some, errs


# ==========================================
# ===            Arrays                 ===
# ==========================================
class Array[T]:
    def __init__(self, iterable: Iterable[T] | None = None) -> None:
        self._data = tuple(iterable or ())

    def count(self, value: T) -> int:
        return self._data.count(value)

    def first(self) -> Maybe[T]:
        return self.get(0)

    def get(self, index: int) -> Maybe[T]:
        try:
            return Some(self._data[index])
        except IndexError:
            return Nothing

    def get_or(self, index: int, default: T) -> T:
        return self.get(index).unwrap_or(default)

    def get_or_else(self, index: int, default_factory: Callable[[], T]) -> T:
        return self.get(index).unwrap_or_else(default_factory)

    def index(self, value: T) -> Maybe[int]:
        try:
            return Some(self._data.index(value))
        except ValueError:
            return Nothing

    def last(self) -> Maybe[T]:
        return self.get(-1)

    def __contains__(self, value: T) -> bool:
        return value in self._data

    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, Array):
            return False
        return tuple(value) == tuple(self)  # type: ignore

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)


class MutArray[T](Array[T]):
    @override
    def __init__(self, iterable: Iterable[T] | None = None) -> None:
        self._data = list(iterable or [])

    def append(self, value: T) -> None:
        self._data.append(value)

    def clear(self) -> None:
        self._data.clear()

    def insert(self, index: int, value: T) -> None:
        self._data.insert(index, value)

    def pop(self, index: int) -> Result[T, errs.IndexErr]:
        try:
            return Ok(self._data.pop(index))
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
            return Ok(self._data.remove(value))
        except ValueError:
            return Err(errs.ValueErr(value, "value not in array"))

    def set(self, index: int, value: T) -> Result[None, errs.IndexErr]:
        try:
            self._data[index] = value
            return Ok(None)
        except IndexError:
            return Err(errs.IndexErr(index))


# ==========================================
# ===            Maps                 ===
# ==========================================
class Map[K, T]:
    def __init__(self, data: Mapping[K, T] | None = None) -> None:
        self._data = data or {}

    def items(self) -> Iterable[tuple[K, T]]:
        return self._data.items()

    def keys(self) -> Iterable[K]:
        return self._data.keys()

    def get(self, key: K) -> Maybe[T]:
        value = self._data.get(key)
        if value is None:
            return Nothing
        return Some(value)

    def get_or(self, key: K, default: T) -> T:
        return self.get(key).unwrap_or(default)

    def get_or_else(self, key: K, default_factory: Callable[[], T]) -> T:
        return self.get(key).unwrap_or_else(default_factory)

    def values(self) -> Iterable[T]:
        return self._data.values()

    def __contains__(self, key: K) -> bool:
        return key in self._data

    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, Map):
            return False
        return value.items() == self.items()

    def __iter__(self) -> Iterator[K]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)


class MutMap[K, T](Map[K, T]):
    @override
    def __init__(self, data: Mapping[K, T] | None = None) -> None:
        self._data = dict(data or {})

    def clear(self) -> None:
        self._data.clear()

    def pop(self, key: K) -> Result[T, errs.KeyErr[K]]:
        try:
            return Ok(self._data.pop(key))
        except KeyError:
            return Err(errs.KeyErr(key))

    def pop_or(self, key: K, default: T) -> T:
        return self.pop(key).unwrap_or(default)

    def pop_or_else(self, key: K, default_factory: Callable[[], T]) -> T:
        return self.pop(key).ok().unwrap_or_else(default_factory)

    def set(self, key: K, value: T) -> None:
        self._data[key] = value

    def set_default(self, key: K, default: T) -> T:
        return self._data.setdefault(key, default)
