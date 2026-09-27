from abc import ABC, abstractmethod
from collections.abc import (
    Callable,
    ItemsView,
    Iterator,
    KeysView,
    Mapping,
    MutableMapping,
    Sequence,
    ValuesView,
)
from dataclasses import dataclass, field
from typing import Any, cast

# ==========================================
# ===            Result                 ===
# ==========================================
type Result[T, E] = Ok[T, E] | Err[E, T]


class _BaseResult[T, E](ABC):
    @abstractmethod
    def and_[U](self, result: Result[U, E]) -> Result[U, E]:
        """Returns `result` if `self` is `Ok`, else returns `self`."""

    @abstractmethod
    def and_then[U](self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Returns result of `func` if `self` is `Ok`, else returns `self`."""

    @abstractmethod
    def inspect(self, func: Callable[[T], Any]) -> Result[T, E]:
        """Calls `func` on `self.value` if `self` is `Ok`, else does nothing. Returns `self`."""

    @abstractmethod
    def inspect_err(self, func: Callable[[E], Any]) -> Result[T, E]:
        """Calls `func` on `self.value` if `self` is `Err`, else does nothing. Returns `self`."""

    @abstractmethod
    def map[U](self, func: Callable[[T], U]) -> Result[U, E]:
        """Returns `Ok` with result of `func` if `self` is `Ok`, else returns `self`."""

    @abstractmethod
    def map_err[F](self, func: Callable[[E], F]) -> Result[T, F]:
        """Returns `Err` with result of `func` if `self` is `Err`, else returns `self`."""

    @abstractmethod
    def map_or[U](self, func: Callable[[T], U], default: U) -> U:
        """Returns result of `func` if `self` is `Ok`, else returns `default`."""

    @abstractmethod
    def map_or_else[U](self, func: Callable[[T], U], default: Callable[[E], U]) -> U:
        """Returns result of `func` if `self` is `Ok`, else returns result of `default`."""

    @abstractmethod
    def ok(self) -> Maybe[T]:
        """Returns `Some` with `self.value` if `self` is `Ok`, else returns `Nothing`."""

    @abstractmethod
    def or_[F](self, result: Result[T, F]) -> Result[T, F]:
        """Returns `result` if `self` is `Err`, else returns `self`."""

    @abstractmethod
    def or_else[F](self, func: Callable[[E], Result[T, F]]) -> Result[T, F]:
        """Returns result of `func` if `self` is `Err`, else returns `self`."""

    @abstractmethod
    def unwrap(self) -> T:
        """Returns `self.value` if `self` is `Ok`, else raises `Panic`."""

    @abstractmethod
    def unwrap_err(self) -> E:
        """Returns `self.value` if `self` is `Err`, else raises `Panic`."""

    @abstractmethod
    def unwrap_or(self, default: T) -> T:
        """Returns `self.value` if `self` is `Ok`, else returns `default`."""

    @abstractmethod
    def unwrap_or_else(self, func: Callable[[E], T]) -> T:
        """Returns `self.value` if `self` is `Ok`, else returns result of `func`."""


@dataclass(frozen=True, slots=True)
class Ok[T, E = Any](_BaseResult[T, E]):
    value: T

    def and_[U](self, result: Result[U, E]) -> Result[U, E]:
        return result

    def and_then[U](self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return func(self.value)

    def inspect(self, func: Callable[[T], Any]) -> Result[T, E]:
        func(self.value)
        return self

    def inspect_err(self, func: Callable[[E], Any]) -> Result[T, E]:
        return self

    def map[U](self, func: Callable[[T], U]) -> Result[U, E]:
        return Ok(func(self.value))

    def map_err[F](self, func: Callable[[E], F]) -> Result[T, F]:
        return cast(Result[T, F], self)

    def map_or[U](self, func: Callable[[T], U], default: U) -> U:
        return func(self.value)

    def map_or_else[U](self, func: Callable[[T], U], default: Callable[[E], U]) -> U:
        return func(self.value)

    def ok(self) -> Maybe[T]:
        return Some(self.value)

    def or_[F](self, result: Result[T, F]) -> Result[T, F]:
        return cast(Result[T, F], self)

    def or_else[F](self, func: Callable[[E], Result[T, F]]) -> Result[T, F]:
        return cast(Result[T, F], self)

    def unwrap(self) -> T:
        return self.value

    def unwrap_err(self) -> E:
        raise Panic(f"called Result.unwrap_err() on Ok value: {self.value}")

    def unwrap_or(self, default: T) -> T:
        return self.value

    def unwrap_or_else(self, func: Callable[[E], T]) -> T:
        return self.value


@dataclass(frozen=True, slots=True)
class Err[E, T = Any](_BaseResult[T, E]):
    value: E

    def and_[U](self, result: Result[U, E]) -> Result[U, E]:
        return cast(Result[U, E], self)

    def and_then[U](self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return cast(Result[U, E], self)

    def inspect(self, func: Callable[[T], Any]) -> Result[T, E]:
        return self

    def inspect_err(self, func: Callable[[E], Any]) -> Result[T, E]:
        func(self.value)
        return self

    def map[U](self, func: Callable[[T], U]) -> Result[U, E]:
        return cast(Result[U, E], self)

    def map_err[F](self, func: Callable[[E], F]) -> Result[T, F]:
        return Err(func(self.value))

    def map_or[U](self, func: Callable[[T], U], default: U) -> U:
        return default

    def map_or_else[U](self, func: Callable[[T], U], default: Callable[[E], U]) -> U:
        return default(self.value)

    def ok(self) -> Maybe[T]:
        return Nothing

    def or_[F](self, result: Result[T, F]) -> Result[T, F]:
        return result

    def or_else[F](self, func: Callable[[E], Result[T, F]]) -> Result[T, F]:
        return func(self.value)

    def unwrap(self) -> T:
        raise Panic(f"called Result.unwrap() on Err value: {self.value}")

    def unwrap_err(self) -> E:
        return self.value

    def unwrap_or(self, default: T) -> T:
        return default

    def unwrap_or_else(self, func: Callable[[E], T]) -> T:
        return func(self.value)


# ==========================================
# ===            Maybe                 ===
# ==========================================
type Maybe[T] = Some[T] | NothingType[T]


class _BaseMaybe[T](ABC):
    @abstractmethod
    def and_[U](self, maybe: Maybe[U]) -> Maybe[U]:
        """Returns `maybe` if `self` is `Some`, else returns `Nothing`."""

    @abstractmethod
    def and_then[U](self, func: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """Returns result of `func` if `self` is `Some`, else returns `Nothing`."""

    @abstractmethod
    def filter(self, predicate: Callable[[T], bool]) -> Maybe[T]:
        """Returns `self` if `self` is `Some` and result of `predicate` is `True`, else returns `Nothing`."""

    @abstractmethod
    def inspect(self, func: Callable[[T], Any]) -> Maybe[T]:
        """Calls `func` on `self.value` if `self` is `Some`, else does nothing. Returns `self`."""

    @abstractmethod
    def map[U](self, func: Callable[[T], U]) -> Maybe[U]:
        """Returns `Some` with result of `func` if `self` is `Some`, else returns `Nothing`."""

    @abstractmethod
    def map_or[U](self, func: Callable[[T], U], default: U) -> U:
        """Returns result of `func` if `self` is `Some`, else returns `default`."""

    @abstractmethod
    def map_or_else[U](self, func: Callable[[T], U], default: Callable[[], U]) -> U:
        """Returns result of `func` if `self` is `Some`, else returns result of `default`."""

    @abstractmethod
    def ok_or[E](self, err: E) -> Result[T, E]:
        """Returns `Ok` with `self.value` if `self` is `Some`, else returns `Err` with `err`."""

    @abstractmethod
    def ok_or_else[E](self, func: Callable[[], E]) -> Result[T, E]:
        """Returns `Ok` with `self.value` if `self` is `Some`, else returns `Err` with result of `func`."""

    @abstractmethod
    def or_[U](self, maybe: Maybe[U]) -> Maybe[U]:
        """Returns `maybe` if `self` is `Nothing`, else returns `self`."""

    @abstractmethod
    def or_else[U](self, func: Callable[[], Maybe[U]]) -> Maybe[U]:
        """Returns result of `func` if `self` is `Nothing`, else returns `self`."""

    @abstractmethod
    def unwrap(self) -> T:
        """Returns `self.value` if `self` is `Some`, else raises `Panic`."""

    @abstractmethod
    def unwrap_or(self, default: T) -> T:
        """Returns `self.value` if `self` is `Some`, else returns `default`."""

    @abstractmethod
    def unwrap_or_else(self, func: Callable[[], T]) -> T:
        """Returns `self.value` if `self` is `Some`, else returns result of `func`."""


@dataclass(frozen=True, slots=True)
class Some[T](_BaseMaybe[T]):
    value: T

    def and_[U](self, maybe: Maybe[U]) -> Maybe[U]:
        return maybe

    def and_then[U](self, func: Callable[[T], Maybe[U]]) -> Maybe[U]:
        return func(self.value)

    def filter(self, predicate: Callable[[T], bool]) -> Maybe[T]:
        return self if predicate(self.value) else Nothing

    def inspect(self, func: Callable[[T], Any]) -> Maybe[T]:
        func(self.value)
        return self

    def map[U](self, func: Callable[[T], U]) -> Maybe[U]:
        return Some(func(self.value))

    def map_or[U](self, func: Callable[[T], U], default: U) -> U:
        return func(self.value)

    def map_or_else[U](self, func: Callable[[T], U], default: Callable[[], U]) -> U:
        return func(self.value)

    def ok_or[E](self, err: E) -> Result[T, E]:
        return Ok(self.value)

    def ok_or_else[E](self, func: Callable[[], E]) -> Result[T, E]:
        return Ok(self.value)

    def or_[U](self, maybe: Maybe[U]) -> Maybe[U]:
        return cast(Maybe[U], self)

    def or_else[U](self, func: Callable[[], Maybe[U]]) -> Maybe[U]:
        return cast(Maybe[U], self)

    def unwrap(self) -> T:
        return self.value

    def unwrap_or(self, default: T) -> T:
        return self.value

    def unwrap_or_else(self, func: Callable[[], T]) -> T:
        return self.value


@dataclass(frozen=True, slots=True)
class NothingType[T = Any](_BaseMaybe[T]):
    value: None = field(default=None, init=False)

    def and_[U](self, maybe: Maybe[U]) -> Maybe[U]:
        return Nothing

    def and_then[U](self, func: Callable[[T], Maybe[U]]) -> Maybe[U]:
        return Nothing

    def filter(self, predicate: Callable[[T], bool]) -> Maybe[T]:
        return Nothing

    def inspect(self, func: Callable[[T], Any]) -> Maybe[T]:
        return Nothing

    def map[U](self, func: Callable[[T], U]) -> Maybe[U]:
        return Nothing

    def map_or[U](self, func: Callable[[T], U], default: U) -> U:
        return default

    def map_or_else[U](self, func: Callable[[T], U], default: Callable[[], U]) -> U:
        return default()

    def ok_or[E](self, err: E) -> Result[T, E]:
        return Err(err)

    def ok_or_else[E](self, func: Callable[[], E]) -> Result[T, E]:
        return Err(func())

    def or_[U](self, maybe: Maybe[U]) -> Maybe[U]:
        return maybe

    def or_else[U](self, func: Callable[[], Maybe[U]]) -> Maybe[U]:
        return func()

    def unwrap(self) -> T:
        raise Panic("called Maybe.unwrap() on Nothing")

    def unwrap_or(self, default: T) -> T:
        return default

    def unwrap_or_else(self, func: Callable[[], T]) -> T:
        return func()


Nothing = NothingType()


# ==========================================
# ===            Panic                 ===
# ==========================================
@dataclass(frozen=True, slots=True)
class Panic(BaseException):
    message: str


# ==========================================
# ===            Map                 ===
# ==========================================
@dataclass(frozen=True, slots=True)
class Map[K, T]:
    data: Mapping[K, T]

    def get(self, key: K) -> Maybe[T]:
        """Returns `Some` with value of type `T` if `key` in `self`, else returns `Nothing`."""
        return self[key].ok()

    def get_or(self, key: K, default: T) -> T:
        """Returns value of type `T` if `key` in `self`, else returns `default`."""
        return self[key].unwrap_or(default)

    def items(self) -> ItemsView[K, T]:
        return self.data.items()

    def keys(self) -> KeysView[K]:
        return self.data.keys()

    def values(self) -> ValuesView[T]:
        return self.data.values()

    def __bool__(self) -> bool:
        return bool(self.data)

    def __contains__(self, key: K) -> bool:
        return key in self.data

    def __getitem__(self, key: K) -> Result[T, KeyError]:
        try:
            return Ok(self.data[key])

        except KeyError as e:
            return Err(e)

    def __iter__(self) -> Iterator[K]:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)


@dataclass(frozen=True, slots=True)
class MutMap[K, T](Map[K, T]):
    data: MutableMapping[K, T] = field(default_factory=dict[K, T])

    def clear(self) -> None:
        self.data.clear()

    def pop(self, key: K) -> Result[T, KeyError]:
        try:
            return Ok(self.data.pop(key))

        except KeyError as e:
            return Err(e)

    def pop_or(self, key: K, default: T) -> T:
        return self.data.pop(key, default)

    def setdefault(self, key: K, default: T) -> T:
        return self.data.setdefault(key, default)

    def __delitem__(self, key: K) -> None:
        del self.data[key]

    def __setitem__(self, key: K, value: T) -> None:
        self.data[key] = value


# ==========================================
# ===            Array                 ===
# ==========================================
@dataclass(frozen=True, slots=True)
class Array[T]:
    data: Sequence[T]

    def count(self, value: T) -> int:
        return self.data.count(value)

    def __bool__(self) -> bool:
        return bool(self.data)

    def __contains__(self, value: T) -> bool:
        return value in self.data

    def __getitem__(self, index: int) -> Result[T, IndexError]:
        try:
            return Ok(self.data[index])

        except IndexError as e:
            return Err(e)

    def __iter__(self) -> Iterator[T]:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)
