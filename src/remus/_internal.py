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

        `Result.and_` is eagerly loaded, for lazy loading, use `Result.and_then`
        """

    @abstractmethod
    def and_then[U](self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Calls `func` and returns its return value if self is an instance of `Ok`, otherwise returns `self`."""

    @abstractmethod
    def expect(self, message: str) -> T:
        """Returns `self.value` if `self` is an instance of `Ok`, otherwise panics with your custom `message`."""


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
