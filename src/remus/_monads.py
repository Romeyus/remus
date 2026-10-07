from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, cast, override

# ==========================================
# ===            Maybe                 ===
# ==========================================
type Maybe[T] = Some[T] | NothingType[T]


class _BaseMaybe[T](ABC):
    @abstractmethod
    def and_[U](self, maybe: Maybe[U]) -> Maybe[U]: ...
    @abstractmethod
    def and_then[U](self, func: Callable[[T], Maybe[U]]) -> Maybe[U]: ...
    @abstractmethod
    def filter(self, predicate: Callable[[T], bool]) -> Maybe[T]: ...
    @abstractmethod
    def inspect(self, func: Callable[[T], Any]) -> Maybe[T]: ...
    @abstractmethod
    def map[U](self, func: Callable[[T], U]) -> Maybe[U]: ...
    @abstractmethod
    def ok_or[E](self, err: E) -> Result[T, E]: ...
    @abstractmethod
    def ok_or_else[E](self, func: Callable[[], E]) -> Result[T, E]: ...
    @abstractmethod
    def or_(self, maybe: Maybe[T]) -> Maybe[T]: ...
    @abstractmethod
    def or_else(self, func: Callable[[], Maybe[T]]) -> Maybe[T]: ...
    @abstractmethod
    def unwrap(self) -> T: ...
    @abstractmethod
    def unwrap_or(self, default: T) -> T: ...
    @abstractmethod
    def unwrap_or_else(self, func: Callable[[], T]) -> T: ...


@dataclass(frozen=True, slots=True)
class Some[T: Any](_BaseMaybe[T]):
    value: T

    @override
    def and_[U](self, maybe: Maybe[U]) -> Maybe[U]:
        return maybe

    @override
    def and_then[U](self, func: Callable[[T], Maybe[U]]) -> Maybe[U]:
        return func(self.value)

    @override
    def filter(self, predicate: Callable[[T], bool]) -> Maybe[T]:
        return self if predicate(self.value) else Nothing

    @override
    def inspect(self, func: Callable[[T], Any]) -> Maybe[T]:
        func(self.value)
        return self

    @override
    def map[U](self, func: Callable[[T], U]) -> Maybe[U]:
        return Some(func(self.value))

    @override
    def ok_or[E](self, err: E) -> Result[T, E]:
        return Ok(self.value)

    @override
    def ok_or_else[E](self, func: Callable[[], E]) -> Result[T, E]:
        return Ok(self.value)

    @override
    def or_(self, maybe: Maybe[T]) -> Maybe[T]:
        return self

    @override
    def or_else(self, func: Callable[[], Maybe[T]]) -> Maybe[T]:
        return self

    @override
    def unwrap(self) -> T:
        return self.value

    @override
    def unwrap_or(self, default: T) -> T:
        return self.value

    @override
    def unwrap_or_else(self, func: Callable[[], T]) -> T:
        return self.value


@dataclass(frozen=True, slots=True)
class NothingType[T = Any](_BaseMaybe[T]):
    value: None = field(default=None, init=False)

    @override
    def and_[U](self, maybe: Maybe[U]) -> Maybe[U]:
        return cast(Maybe[U], self)

    @override
    def and_then[U](self, func: Callable[[T], Maybe[U]]) -> Maybe[U]:
        return cast(Maybe[U], self)

    @override
    def filter(self, predicate: Callable[[T], bool]) -> Maybe[T]:
        return self

    @override
    def inspect(self, func: Callable[[T], Any]) -> Maybe[T]:
        return self

    @override
    def map[U](self, func: Callable[[T], U]) -> Maybe[U]:
        return cast(Maybe[U], self)

    @override
    def ok_or[E](self, err: E) -> Result[T, E]:
        return Err(err)

    @override
    def ok_or_else[E](self, func: Callable[[], E]) -> Result[T, E]:
        return Err(func())

    @override
    def or_(self, maybe: Maybe[T]) -> Maybe[T]:
        return maybe

    @override
    def or_else(self, func: Callable[[], Maybe[T]]) -> Maybe[T]:
        return func()

    @override
    def unwrap(self) -> T:
        raise Panic("Called Maybe.unwrap() on Nothing.")

    @override
    def unwrap_or(self, default: T) -> T:
        return default

    @override
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
# ===            Result                 ===
# ==========================================
type Result[T, E] = Ok[T, E] | Err[E, T]


class _BaseResult[T, E](ABC):
    @abstractmethod
    def and_[U](self, result: Result[U, E]) -> Result[U, E]: ...
    @abstractmethod
    def and_then[U](self, func: Callable[[T], Result[U, E]]) -> Result[U, E]: ...
    @abstractmethod
    def err(self) -> Maybe[E]: ...
    @abstractmethod
    def inspect(self, func: Callable[[T], Any]) -> Result[T, E]: ...
    @abstractmethod
    def inspect_err(self, func: Callable[[E], Any]) -> Result[T, E]: ...
    @abstractmethod
    def map[U](self, func: Callable[[T], U]) -> Result[U, E]: ...
    @abstractmethod
    def map_err[F](self, func: Callable[[E], F]) -> Result[T, F]: ...
    @abstractmethod
    def map_or[U](self, func: Callable[[T], U], default: U) -> U: ...
    @abstractmethod
    def map_or_else[U](
        self, func: Callable[[T], U], default: Callable[[E], U]
    ) -> U: ...
    @abstractmethod
    def ok(self) -> Maybe[T]: ...
    @abstractmethod
    def or_[F](self, result: Result[T, F]) -> Result[T, F]: ...
    @abstractmethod
    def or_else[F](self, func: Callable[[E], Result[T, F]]) -> Result[T, F]: ...
    @abstractmethod
    def unwrap(self) -> T: ...
    @abstractmethod
    def unwrap_err(self) -> E: ...
    @abstractmethod
    def unwrap_or(self, default: T) -> T: ...
    @abstractmethod
    def unwrap_or_else(self, func: Callable[[E], T]) -> T: ...


@dataclass(frozen=True, slots=True)
class Ok[T, E = Any](_BaseResult[T, E]):
    value: T

    @override
    def and_[U](self, result: Result[U, E]) -> Result[U, E]:
        return result

    @override
    def and_then[U](self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return func(self.value)

    @override
    def err(self) -> Maybe[E]:
        return Nothing

    @override
    def inspect(self, func: Callable[[T], Any]) -> Result[T, E]:
        func(self.value)
        return self

    @override
    def inspect_err(self, func: Callable[[E], Any]) -> Result[T, E]:
        return self

    @override
    def map[U](self, func: Callable[[T], U]) -> Result[U, E]:
        return Ok(func(self.value))

    @override
    def map_err[F](self, func: Callable[[E], F]) -> Result[T, F]:
        return cast(Result[T, F], self)

    @override
    def map_or[U](self, func: Callable[[T], U], default: U) -> U:
        return func(self.value)

    @override
    def map_or_else[U](self, func: Callable[[T], U], default: Callable[[E], U]) -> U:
        return func(self.value)

    @override
    def ok(self) -> Maybe[T]:
        return Some(self.value)

    @override
    def or_[F](self, result: Result[T, F]) -> Result[T, F]:
        return cast(Result[T, F], self)

    @override
    def or_else[F](self, func: Callable[[E], Result[T, F]]) -> Result[T, F]:
        return cast(Result[T, F], self)

    @override
    def unwrap(self) -> T:
        return self.value

    @override
    def unwrap_err(self) -> E:
        raise Panic(f"Called Result.unwrap_err() on an Ok value, {self.value}.")

    @override
    def unwrap_or(self, default: T) -> T:
        return self.value

    @override
    def unwrap_or_else(self, func: Callable[[E], T]) -> T:
        return self.value


@dataclass(frozen=True, slots=True)
class Err[E, T = Any](_BaseResult[T, E]):
    value: E

    @override
    def and_[U](self, result: Result[U, E]) -> Result[U, E]:
        return cast(Result[U, E], self)

    @override
    def and_then[U](self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return cast(Result[U, E], self)

    @override
    def err(self) -> Maybe[E]:
        return Some(self.value)

    @override
    def inspect(self, func: Callable[[T], Any]) -> Result[T, E]:
        return self

    @override
    def inspect_err(self, func: Callable[[E], Any]) -> Result[T, E]:
        func(self.value)
        return self

    @override
    def map[U](self, func: Callable[[T], U]) -> Result[U, E]:
        return cast(Result[U, E], self)

    @override
    def map_err[F](self, func: Callable[[E], F]) -> Result[T, F]:
        return Err(func(self.value))

    @override
    def map_or[U](self, func: Callable[[T], U], default: U) -> U:
        return default

    @override
    def map_or_else[U](self, func: Callable[[T], U], default: Callable[[E], U]) -> U:
        return default(self.value)

    @override
    def ok(self) -> Maybe[T]:
        return Nothing

    @override
    def or_[F](self, result: Result[T, F]) -> Result[T, F]:
        return result

    @override
    def or_else[F](self, func: Callable[[E], Result[T, F]]) -> Result[T, F]:
        return func(self.value)

    @override
    def unwrap(self) -> T:
        raise Panic(f"Called Result.unwrap() on an Err value, {self.value}.")

    @override
    def unwrap_err(self) -> E:
        return self.value

    @override
    def unwrap_or(self, default: T) -> T:
        return default

    @override
    def unwrap_or_else(self, func: Callable[[E], T]) -> T:
        return func(self.value)
