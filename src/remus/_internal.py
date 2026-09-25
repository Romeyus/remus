from abc import ABC, abstractmethod
from collections.abc import Callable
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
    def or_[F](self, result: Result[T, F]) -> Result[T, F]:
        """Returns `result` if `self` is `Err`, else returns `self`."""

    @abstractmethod
    def or_else[F](self, func: Callable[[E], Result[T, F]]) -> Result[T, F]:
        """Returns result of `func` if `self` is `Err`, else returns `self`."""

    @abstractmethod
    def unwrap(self) -> T:
        """Returns `self.value` if `self` is `Ok`, else raises `Panic`."""

    @abstractmethod
    def unwrap_or(self, default: T) -> T:
        """Returns `self.value` if `self` is `Ok`, else returns `default`."""


@dataclass(frozen=True, slots=True)
class Ok[T, E = Any](_BaseResult[T, E]):
    value: T

    def and_[U](self, result: Result[U, E]) -> Result[U, E]:
        return result

    def and_then[U](self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return func(self.value)

    def or_[F](self, result: Result[T, F]) -> Result[T, F]:
        return cast(Result[T, F], self)

    def or_else[F](self, func: Callable[[E], Result[T, F]]) -> Result[T, F]:
        return cast(Result[T, F], self)

    def unwrap(self) -> T:
        return self.value

    def unwrap_or(self, default: T) -> T:
        return self.value


@dataclass(frozen=True, slots=True)
class Err[E, T = Any](_BaseResult[T, E]):
    value: E

    def and_[U](self, result: Result[U, E]) -> Result[U, E]:
        return cast(Result[U, E], self)

    def and_then[U](self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return cast(Result[U, E], self)

    def or_[F](self, result: Result[T, F]) -> Result[T, F]:
        return result

    def or_else[F](self, func: Callable[[E], Result[T, F]]) -> Result[T, F]:
        return func(self.value)

    def unwrap(self) -> T:
        raise Panic(f"called Result.unwrap() on Err value: {self.value}")

    def unwrap_or(self, default: T) -> T:
        return default


# ==========================================
# ===            Maybe                 ===
# ==========================================
type Maybe[T] = Some[T] | Nothing[T]


class _BaseMaybe[T](ABC): ...


@dataclass(frozen=True, slots=True)
class Some[T](_BaseMaybe[T]):
    value: T


@dataclass(frozen=True, slots=True)
class Nothing[T = Any](_BaseMaybe[T]):
    value: None = field(default=None, init=False)


# ==========================================
# ===            Panic                 ===
# ==========================================
@dataclass(frozen=True, slots=True)
class Panic(BaseException):
    message: str
