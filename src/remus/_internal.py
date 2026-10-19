import logging
import sys
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from threading import current_thread
from traceback import format_exception
from types import TracebackType
from typing import Any, Never, cast, final, override

# ==========================================
# ===            Constants                 ===
# ==========================================
PANIC_FONT_RED_BOLD = "\x1b[1;31m"
PANIC_FONT_RESET = "\x1b[0m"

logger = logging.getLogger("remus")


# ==========================================
# ===            Types                 ===
# ==========================================
type Result[T, E] = Ok[T, E] | Err[E, T]
type Maybe[T] = Some[T] | NothingType[T]


# ==========================================
# ===            Panic                 ===
# ==========================================
@final
class Panic(BaseException):
    def __init__(self, message: str) -> None:
        self._message = message

    def __str__(self) -> str:
        return self._message


def panic(message: str) -> Never:
    raise Panic(message)


def panic_excepthook(  # pragma: no cover
    exc_type: type[BaseException], exc: BaseException, traceback: TracebackType | None
) -> None:
    if not isinstance(exc, Panic):
        return sys.__excepthook__(exc_type, exc, traceback)

    logger.critical("\n" + "".join(format_exception(exc)))
    logger.critical(
        f"\n{PANIC_FONT_RED_BOLD}thread '{current_thread().name}' panicked: '{exc}'"
        f"{PANIC_FONT_RESET}\n"
    )


sys.excepthook = panic_excepthook


# ==========================================
# ===            Result                 ===
# ==========================================
class _BaseResult[T, E](ABC):
    @abstractmethod
    def and_[U](self, result: Result[U, E]) -> Result[U, E]:
        """
        Returns `result` if `self` is an instance of `Ok`, otherwise returns `self`.

        `Result.and_` is eagerly loaded, for lazy loading, use `Result.and_then`.
        """

    @abstractmethod
    def and_then[U](self, factory: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Calls `factory` and returns its return value if self is an instance of `Ok`, otherwise returns `self`."""

    @abstractmethod
    def err(self) -> Maybe[E]:
        """Returns `Some` with `self.value` if `self` is an instance of `Err`, otherwise returns `Nothing`."""

    @abstractmethod
    def expect(self, message: str) -> T:
        """Returns `self.value` if `self` is an instance of `Ok`, otherwise panics with your custom `message`."""

    @abstractmethod
    def expect_err(self, message: str) -> E:
        """Returns `self.value` if `self` is an instance of `Err`, otherwise panics with your custom `message`."""

    @abstractmethod
    def inspect(self, func: Callable[[T], Any]) -> Result[T, E]:
        """Calls `func` with `self.value` if `self` is an instance of `Ok`."""

    @abstractmethod
    def inspect_err(self, func: Callable[[E], Any]) -> Result[T, E]:
        """Calls `func` with `self.value` if `self` is an instance of `Err`."""

    @abstractmethod
    def map[U](self, factory: Callable[[T], U]) -> Result[U, E]:
        """Calls `factory` with `self.value` and returns a new `Ok` instance with the return value of `factory` if `self` is an instance of `Ok`, otherwise returns `self`."""

    @abstractmethod
    def map_err[F](self, factory: Callable[[E], F]) -> Result[T, F]:
        """Calls `factory` with `self.value` and returns a new `Err` instance with the return value of `factory` if `self` is an instance of `Err`, otherwise returns `self`."""

    @abstractmethod
    def map_or[U](self, factory: Callable[[T], U], default: U) -> U:
        """Calls `factory` with `self.value` and returns the return value of `factory` if `self` is an instance of `Ok`, otherwise returns `default`."""

    @abstractmethod
    def map_or_else[U](
        self, factory: Callable[[T], U], default_factory: Callable[[E], U]
    ) -> U:
        """Calls `factory` with `self.value` and returns the return value of `factory` if `self` is an instance of `Ok`, otherwise calls `default_factory` with `self.value` and returns the return value of `default_factory`."""

    @abstractmethod
    def ok(self) -> Maybe[T]:
        """Returns `Some` with `self.value` if `self` is an instance of `Ok`, otherwise returns `Nothing`."""

    @abstractmethod
    def or_[F](self, result: Result[T, F]) -> Result[T, F]:
        """
        Returns `result` if `self` is an instance of `Err`, otherwise returns `self`.

        `Result.or_` is eagerly loaded, for lazy loading, use `Result.or_else`.
        """

    @abstractmethod
    def or_else[F](self, factory: Callable[[E], Result[T, F]]) -> Result[T, F]:
        """Calls `factory` and returns its return value if self is an instance of `Err`, otherwise returns `self`."""

    @abstractmethod
    def unwrap(self) -> T:
        """Returns `self.value` if `self` is an instance of `Ok`, otherwise panics."""

    @abstractmethod
    def unwrap_err(self) -> E:
        """Returns `self.value` if `self` is an instance of `Err`, otherwise panics."""

    @abstractmethod
    def unwrap_or(self, default: T) -> T:
        """Returns `self.value` if `self` is an instance of `Ok`, otherwise returns `default`."""

    @abstractmethod
    def unwrap_or_else(self, default_factory: Callable[[E], T]) -> T:
        """Returns `self.value` if `self` is an instance of `Ok`, otherwise calls `default_factory` with `self.value` and returns the return value of `default_factory`."""


@final
@dataclass(frozen=True, slots=True)
class Ok[T, E = Any](_BaseResult[T, E]):
    value: T

    @override
    def and_[U](self, result: Result[U, E]) -> Result[U, E]:
        return result

    @override
    def and_then[U](self, factory: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return factory(self.value)

    @override
    def err(self) -> Maybe[E]:
        return Nothing

    @override
    def expect(self, message: str) -> T:
        return self.value

    @override
    def expect_err(self, message: str) -> E:
        panic(f"{message}: {self.value}")

    @override
    def inspect(self, func: Callable[[T], Any]) -> Result[T, E]:
        func(self.value)
        return self

    @override
    def inspect_err(self, func: Callable[[E], Any]) -> Result[T, E]:
        return self

    @override
    def map[U](self, factory: Callable[[T], U]) -> Result[U, E]:
        return Ok(factory(self.value))

    @override
    def map_err[F](self, factory: Callable[[E], F]) -> Result[T, F]:
        return cast(Result[T, F], self)

    @override
    def map_or[U](self, factory: Callable[[T], U], default: U) -> U:
        return factory(self.value)

    @override
    def map_or_else[U](
        self, factory: Callable[[T], U], default_factory: Callable[[E], U]
    ) -> U:
        return factory(self.value)

    @override
    def ok(self) -> Maybe[T]:
        return Some(self.value)

    @override
    def or_[F](self, result: Result[T, F]) -> Result[T, F]:
        return cast(Result[T, F], self)

    @override
    def or_else[F](self, factory: Callable[[E], Result[T, F]]) -> Result[T, F]:
        return cast(Result[T, F], self)

    @override
    def unwrap(self) -> T:
        return self.value

    @override
    def unwrap_err(self) -> E:
        panic(f"called Result.unwrap_err() on an Ok value, {self.value}")

    @override
    def unwrap_or(self, default: T) -> T:
        return self.value

    @override
    def unwrap_or_else(self, default_factory: Callable[[E], T]) -> T:
        return self.value


@final
@dataclass(frozen=True, slots=True)
class Err[E, T = Any](_BaseResult[T, E]):
    value: E

    @override
    def and_[U](self, result: Result[U, E]) -> Result[U, E]:
        return cast(Result[U, E], self)

    @override
    def and_then[U](self, factory: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return cast(Result[U, E], self)

    @override
    def err(self) -> Maybe[E]:
        return Some(self.value)

    @override
    def expect(self, message: str) -> T:
        panic(f"{message}: {self.value}")

    @override
    def expect_err(self, message: str) -> E:
        return self.value

    @override
    def inspect(self, func: Callable[[T], Any]) -> Result[T, E]:
        return self

    @override
    def inspect_err(self, func: Callable[[E], Any]) -> Result[T, E]:
        func(self.value)
        return self

    @override
    def map[U](self, factory: Callable[[T], U]) -> Result[U, E]:
        return cast(Result[U, E], self)

    @override
    def map_err[F](self, factory: Callable[[E], F]) -> Result[T, F]:
        return Err(factory(self.value))

    @override
    def map_or[U](self, factory: Callable[[T], U], default: U) -> U:
        return default

    @override
    def map_or_else[U](
        self, factory: Callable[[T], U], default_factory: Callable[[E], U]
    ) -> U:
        return default_factory(self.value)

    @override
    def ok(self) -> Maybe[T]:
        return Nothing

    @override
    def or_[F](self, result: Result[T, F]) -> Result[T, F]:
        return result

    @override
    def or_else[F](self, factory: Callable[[E], Result[T, F]]) -> Result[T, F]:
        return factory(self.value)

    @override
    def unwrap(self) -> T:
        panic(f"called Result.unwrap() on an Err value, {self.value}")

    @override
    def unwrap_err(self) -> E:
        return self.value

    @override
    def unwrap_or(self, default: T) -> T:
        return default

    @override
    def unwrap_or_else(self, default_factory: Callable[[E], T]) -> T:
        return default_factory(self.value)


# ==========================================
# ===            Maybe                 ===
# ==========================================
class _BaseMaybe[T](ABC):
    @abstractmethod
    def and_[U](self, maybe: Maybe[U]) -> Maybe[U]:
        """
        Returns `maybe` if `self` is an instance of `Some`, otherwise returns `Nothing`.

        `Maybe.and_` is eagerly loaded, for lazy loading, use `Maybe.and_then`.
        """

    @abstractmethod
    def and_then[U](self, factory: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """Calls `factory` and returns its return value if self is an instance of `Some`, otherwise returns `Nothing`."""

    @abstractmethod
    def expect(self, message: str) -> T:
        """Returns `self.value` if `self` is an instance of `Some`, otherwise panics with your custom `message`."""

    @abstractmethod
    def filter(self, predicate: Callable[[T], bool]) -> Maybe[T]:
        """Returns `self` if `self` is an instance of `Some` and the return value of `predicate` with `self.value` is `True`, otherwise returns `Nothing`."""

    @abstractmethod
    def inspect(self, func: Callable[[T], Any]) -> Maybe[T]:
        """Calls `func` with `self.value` if `self` is an instance of `Some`."""

    @abstractmethod
    def map[U](self, factory: Callable[[T], U]) -> Maybe[U]:
        """Calls `factory` with `self.value` and returns a new `Some` instance with the return value of `factory` if `self` is an instance of `Some`, otherwise returns `Nothing`."""

    @abstractmethod
    def map_or[U](self, factory: Callable[[T], U], default: U) -> U:
        """Calls `factory` with `self.value` and returns the return value of `factory` if `self` is an instance of `Some`, otherwise returns `default`."""

    @abstractmethod
    def map_or_else[U](
        self, factory: Callable[[T], U], default_factory: Callable[[], U]
    ) -> U:
        """Calls `factory` with `self.value` and returns the return value of `factory` if `self` is an instance of `Some`, otherwise returns the return value of `default_factory`."""

    @abstractmethod
    def ok_or[E](self, err: E) -> Result[T, E]:
        """Returns an instance of `Ok` with `self.value` if `self` is an instance of `Some`, otherwise returns an instance of `Err` with `err`."""

    @abstractmethod
    def ok_or_else[E](self, factory: Callable[[], E]) -> Result[T, E]:
        """Returns an instance of `Ok` with `self.value` if `self` is an instance of `Some`, otherwise returns an instance of `Err` with the return value of `factory`."""

    @abstractmethod
    def or_(self, maybe: Maybe[T]) -> Maybe[T]:
        """
        Returns `maybe` if `self` is `Nothing`, otherwise returns `self`.

        `Maybe.or_` is eagerly loaded, for lazy loading, use `Maybe.or_else`.
        """

    @abstractmethod
    def or_else(self, factory: Callable[[], Maybe[T]]) -> Maybe[T]:
        """Calls `factory` and returns its return value if `self` is `Nothing`, otherwise returns `self`."""

    @abstractmethod
    def unwrap(self) -> T:
        """Returns `self.value` if `self` is an instance of `Some`, otherwise panics."""

    @abstractmethod
    def unwrap_or(self, default: T) -> T:
        """Returns `self.value` if `self` is an instance of `Some`, otherwise returns `default`."""

    @abstractmethod
    def unwrap_or_else(self, factory: Callable[[], T]) -> T:
        """Returns `self.value` if `self` is an instance of `Some`, otherwise returns the return value of `factory`."""


@final
@dataclass(frozen=True, slots=True)
class Some[T](_BaseMaybe[T]):
    value: T

    @override
    def and_[U](self, maybe: Maybe[U]) -> Maybe[U]:
        return maybe

    @override
    def and_then[U](self, factory: Callable[[T], Maybe[U]]) -> Maybe[U]:
        return factory(self.value)

    @override
    def expect(self, message: str) -> T:
        return self.value

    @override
    def filter(self, predicate: Callable[[T], bool]) -> Maybe[T]:
        return self if predicate(self.value) else Nothing

    @override
    def inspect(self, func: Callable[[T], Any]) -> Maybe[T]:
        func(self.value)
        return self

    @override
    def map[U](self, factory: Callable[[T], U]) -> Maybe[U]:
        return Some(factory(self.value))

    @override
    def map_or[U](self, factory: Callable[[T], U], default: U) -> U:
        return factory(self.value)

    @override
    def map_or_else[U](
        self, factory: Callable[[T], U], default_factory: Callable[[], U]
    ) -> U:
        return factory(self.value)

    @override
    def ok_or[E](self, err: E) -> Result[T, E]:
        return Ok(self.value)

    @override
    def ok_or_else[E](self, factory: Callable[[], E]) -> Result[T, E]:
        return Ok(self.value)

    @override
    def or_(self, maybe: Maybe[T]) -> Maybe[T]:
        return self

    @override
    def or_else(self, factory: Callable[[], Maybe[T]]) -> Maybe[T]:
        return self

    @override
    def unwrap(self) -> T:
        return self.value

    @override
    def unwrap_or(self, default: T) -> T:
        return self.value

    @override
    def unwrap_or_else(self, factory: Callable[[], T]) -> T:
        return self.value


@final
@dataclass(frozen=True, slots=True)
class NothingType[T = Any](_BaseMaybe[T]):
    value: None = field(default=None, init=False)

    @override
    def and_[U](self, maybe: Maybe[U]) -> Maybe[U]:
        return Nothing

    @override
    def and_then[U](self, factory: Callable[[T], Maybe[U]]) -> Maybe[U]:
        return Nothing

    @override
    def expect(self, message: str) -> T:
        panic(message)

    @override
    def filter(self, predicate: Callable[[T], bool]) -> Maybe[T]:
        return Nothing

    @override
    def inspect(self, func: Callable[[T], Any]) -> Maybe[T]:
        return Nothing

    @override
    def map[U](self, factory: Callable[[T], U]) -> Maybe[U]:
        return Nothing

    @override
    def map_or[U](self, factory: Callable[[T], U], default: U) -> U:
        return default

    @override
    def map_or_else[U](
        self, factory: Callable[[T], U], default_factory: Callable[[], U]
    ) -> U:
        return default_factory()

    @override
    def ok_or[E](self, err: E) -> Result[T, E]:
        return Err(err)

    @override
    def ok_or_else[E](self, factory: Callable[[], E]) -> Result[T, E]:
        return Err(factory())

    @override
    def or_(self, maybe: Maybe[T]) -> Maybe[T]:
        return maybe

    @override
    def or_else(self, factory: Callable[[], Maybe[T]]) -> Maybe[T]:
        return factory()

    @override
    def unwrap(self) -> T:
        panic("called Maybe.unwrap() on Nothing")

    @override
    def unwrap_or(self, default: T) -> T:
        return default

    @override
    def unwrap_or_else(self, factory: Callable[[], T]) -> T:
        return factory()


Nothing = NothingType()
