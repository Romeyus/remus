from collections.abc import (
    Callable,
    ItemsView,
    Iterable,
    Iterator,
    KeysView,
    Mapping,
    ValuesView,
)
from dataclasses import dataclass
from typing import Protocol

from remus._monads import Err, Maybe, Ok, Result


# ==========================================
# ===            Array                 ===
# ==========================================
class Array[T](Protocol):
    def count(self, value: T) -> int: ...
    def first(self) -> Maybe[T]: ...
    def first_or(self, default: T) -> T: ...
    def get(self, index: int) -> Maybe[T]: ...
    def get_or(self, index: int, default: T) -> T: ...
    def last(self) -> Maybe[T]: ...
    def last_or(self, default: T) -> T: ...
    def __contains__(self, item: T) -> bool: ...
    def __getitem__(self, index: int) -> Result[T, IndexError]: ...
    def __iter__(self) -> Iterator[T]: ...
    def __len__(self) -> int: ...


@dataclass(frozen=True, slots=True)
class _Array[T]:
    _data: tuple[T, ...]

    def count(self, value: T) -> int:
        return self._data.count(value)

    def first(self) -> Maybe[T]:
        return self.get(0)

    def first_or(self, default: T) -> T:
        return self.get_or(0, default)

    def get(self, index: int) -> Maybe[T]:
        return self[index].ok()

    def get_or(self, index: int, default: T) -> T:
        return self[index].unwrap_or(default)

    def last(self) -> Maybe[T]:
        return self.get(-1)

    def last_or(self, default: T) -> T:
        return self.get_or(-1, default)

    def __contains__(self, item: T) -> bool:
        return item in self._data

    def __getitem__(self, index: int) -> Result[T, IndexError]:
        try:
            return Ok(self._data[index])
        except IndexError as e:
            return Err(e)

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)


def new_array[T](data: Iterable[T] | None = None) -> Array[T]:  # pragma: no cover
    return _Array(tuple(data or ()))


class MutArray[T](Array[T], Protocol):
    def append(self, value: T) -> None: ...
    def insert(self, index: int, value: T) -> None: ...
    def pop(self, index: int) -> Result[T, IndexError]: ...
    def pop_or(self, index: int, default: T) -> T: ...
    def pop_or_else(self, index: int, func: Callable[[], T]) -> T: ...
    def prepend(self, value: T) -> None: ...
    def __delitem__(self, index: int) -> None: ...
    def __setitem__(self, index: int, value: T) -> None: ...


@dataclass(frozen=True, slots=True)
class _MutArray[T](_Array[T]):
    _data: list[T]

    def append(self, value: T) -> None:
        self._data.append(value)

    def insert(self, index: int, value: T) -> None:
        self._data.insert(index, value)

    def pop(self, index: int) -> Result[T, IndexError]:
        try:
            return Ok(self._data.pop(index))
        except IndexError as e:
            return Err(e)

    def pop_or(self, index: int, default: T) -> T:
        return self.pop(index).unwrap_or(default)

    def pop_or_else(self, index: int, func: Callable[[], T]) -> T:
        return self.pop(index).ok().unwrap_or_else(func)

    def prepend(self, value: T) -> None:
        self.insert(0, value)

    def __delitem__(self, index: int) -> None:
        del self._data[index]

    def __setitem__(self, index: int, value: T) -> None:
        self._data[index] = value


def new_mut_array[T](
    data: Iterable[T] | None = None,
) -> MutArray[T]:  # pragma: no cover
    return _MutArray(list(data or []))


# ==========================================
# ===            Map                 ===
# ==========================================
class Map[K, T](Protocol):
    def get(self, key: K) -> Maybe[T]: ...
    def get_or(self, key: K, default: T) -> T: ...
    def get_or_else(self, key: K, func: Callable[[], T]) -> T: ...
    def items(self) -> ItemsView[K, T]: ...
    def keys(self) -> KeysView[K]: ...
    def values(self) -> ValuesView[T]: ...
    def __contains__(self, key: K) -> bool: ...
    def __getitem__(self, key: K) -> Result[T, KeyError]: ...
    def __iter__(self) -> Iterator[K]: ...
    def __len__(self) -> int: ...


@dataclass(frozen=True, slots=True)
class _Map[K, T]:
    _data: frozendict[K, T]

    def get(self, key: K) -> Maybe[T]:
        return self[key].ok()

    def get_or(self, key: K, default: T) -> T:
        return self[key].unwrap_or(default)

    def get_or_else(self, key: K, func: Callable[[], T]) -> T:
        return self.get(key).unwrap_or_else(func)

    def items(self) -> ItemsView[K, T]:
        return self._data.items()

    def keys(self) -> KeysView[K]:
        return self._data.keys()

    def values(self) -> ValuesView[T]:
        return self._data.values()

    def __contains__(self, key: K) -> bool:
        return key in self._data

    def __getitem__(self, key: K) -> Result[T, KeyError]:
        try:
            return Ok(self._data[key])
        except KeyError as e:
            return Err(e)

    def __iter__(self) -> Iterator[K]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)


def new_map[K, T](data: Mapping[K, T] | None = None) -> Map[K, T]:  # pragma: no cover
    return _Map[K, T](frozendict(data or {}))


class MutMap[K, T](Map[K, T], Protocol):
    def insert(self, key: K, value: T) -> Maybe[T]: ...
    def insert_or(self, key: K, default: T) -> T: ...
    def pop(self, key: K) -> Result[T, KeyError]: ...
    def pop_or(self, key: K, default: T) -> T: ...
    def pop_or_else(self, key: K, func: Callable[[], T]) -> T: ...
    def __delitem__(self, key: K) -> None: ...
    def __setitem__(self, key: K, value: T) -> None: ...


@dataclass(frozen=True, slots=True)
class _MutMap[K, T](_Map[K, T]):
    _data: dict[K, T]

    def insert(self, key: K, value: T) -> Maybe[T]:
        return self[key].inspect_err(lambda _: self.__setitem__(key, value)).ok()

    def insert_or(self, key: K, default: T) -> T:
        return self.insert(key, default).unwrap_or(default)

    def pop(self, key: K) -> Result[T, KeyError]:
        try:
            return Ok(self._data.pop(key))
        except KeyError as e:
            return Err(e)

    def pop_or(self, key: K, default: T) -> T:
        return self.pop(key).unwrap_or(default)

    def pop_or_else(self, key: K, func: Callable[[], T]) -> T:
        return self.pop(key).ok().unwrap_or_else(func)

    def __delitem__(self, key: K) -> None:
        del self._data[key]

    def __setitem__(self, key: K, value: T) -> None:
        self._data[key] = value


def new_mut_map[K, T](
    data: Mapping[K, T] | None = None,
) -> MutMap[K, T]:  # pragma: no cover
    return _MutMap(dict(data or {}))
