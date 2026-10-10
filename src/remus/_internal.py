import sys
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from threading import current_thread
from traceback import extract_tb, print_tb
from types import TracebackType
from typing import Any, Never, cast, final, override

# ==========================================
# ===            Constants                 ===
# ==========================================
_PANIC_FONT_RED_BOLD = "\x1b[1;31m"
_PANIC_FONT_RESET = "\x1b[0m"


# ==========================================
# ===            Types                 ===
# ==========================================
type Result[T, E] = Ok[T, E] | Err[E, T]


# ==========================================
# ===            Panic                 ===
# ==========================================
@dataclass(frozen=True, slots=True)
class Panic(BaseException):
    message: str

    def __str__(self) -> str:
        return self.message


def panic(message: str) -> Never:
    raise Panic(message)


def _panic_excepthook(  # pragma: no cover
    exc_type: type[BaseException], exc: BaseException, traceback: TracebackType | None
) -> None:
    if exc_type is not Panic:
        return sys.__excepthook__(exc_type, exc, traceback)

    frames = extract_tb(traceback)[:-1]
    if not frames:
        return print(
            f"thread '{current_thread().name}' panicked at '{exc}'", file=sys.stderr
        )

    print("Traceback (most recent call last):")
    print_tb(traceback, file=sys.stderr, limit=len(frames))

    frame = frames[-1]
    print(
        f"\n{_PANIC_FONT_RED_BOLD}thread '{current_thread().name}' panicked at '{exc}',"
        f" {frame.filename}:{frame.lineno}{_PANIC_FONT_RESET}",
        file=sys.stderr,
    )


sys.excepthook = _panic_excepthook


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
    def and_then[U](self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Calls `func` and returns its return value if self is an instance of `Ok`, otherwise returns `self`."""

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
    def map[U](self, func: Callable[[T], U]) -> Result[U, E]:
        """Calls `func` with `self.value` and returns a new `Ok` instance with the return value of `func` if `self` is an instance of `Ok`, otherwise returns `self`."""

    @abstractmethod
    def map_err[F](self, func: Callable[[E], F]) -> Result[T, F]:
        """Calls `func` with `self.value` and returns a new `Err` instance with the return value of `func` if `self` is an instance of `Err`, otherwise returns `self`."""

    @abstractmethod
    def map_or[U](self, func: Callable[[T], U], default: U) -> U:
        """Calls `func` with `self.value` and returns the return value of `func` if `self` is an instance of `Ok`, otherwise returns `default`."""

    @abstractmethod
    def map_or_else[U](
        self, func: Callable[[T], U], default_factory: Callable[[E], U]
    ) -> U:
        """Calls `func` with `self.value` and returns the return value of `func` if `self` is an instance of `Ok`, otherwise calls `default_factory` with `self.value` and returns the return value of `default_factory`."""

    @abstractmethod
    def or_[F](self, result: Result[T, F]) -> Result[T, F]:
        """
        Returns `result` if `self` is an instance of `Err`, otherwise returns `self`.

        `Result.or_` is eagerly loaded, for lazy loading, use `Result.or_else`.
        """


@final
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
    def map[U](self, func: Callable[[T], U]) -> Result[U, E]:
        return Ok(func(self.value))

    @override
    def map_err[F](self, func: Callable[[E], F]) -> Result[T, F]:
        return cast(Result[T, F], self)

    @override
    def map_or[U](self, func: Callable[[T], U], default: U) -> U:
        return func(self.value)

    @override
    def map_or_else[U](
        self, func: Callable[[T], U], default_factory: Callable[[E], U]
    ) -> U:
        return func(self.value)

    @override
    def or_[F](self, result: Result[T, F]) -> Result[T, F]:
        return cast(Result[T, F], self)


@final
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
    def map[U](self, func: Callable[[T], U]) -> Result[U, E]:
        return cast(Result[U, E], self)

    @override
    def map_err[F](self, func: Callable[[E], F]) -> Result[T, F]:
        return Err(func(self.value))

    @override
    def map_or[U](self, func: Callable[[T], U], default: U) -> U:
        return default

    @override
    def map_or_else[U](
        self, func: Callable[[T], U], default_factory: Callable[[E], U]
    ) -> U:
        return default_factory(self.value)

    @override
    def or_[F](self, result: Result[T, F]) -> Result[T, F]:
        return result
