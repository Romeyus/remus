from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
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
    def or_else[F](self, func: Callable[[E], Result[T, F]]) -> Result[T, F]:
        """Returns result of `func` if `self` is `Err`, else returns `self`."""


@dataclass(frozen=True, slots=True)
class Ok[T, E = Any](_BaseResult[T, E]):
    value: T

    def and_[U](self, result: Result[U, E]) -> Result[U, E]:
        return result

    def and_then[U](self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return func(self.value)

    def or_else[F](self, func: Callable[[E], Result[T, F]]) -> Result[T, F]:
        return cast(Result[T, F], self)


@dataclass(frozen=True, slots=True)
class Err[E, T = Any](_BaseResult[T, E]):
    value: E

    def and_[U](self, result: Result[U, E]) -> Result[U, E]:
        return cast(Result[U, E], self)

    def and_then[U](self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return cast(Result[U, E], self)

    def or_else[F](self, func: Callable[[E], Result[T, F]]) -> Result[T, F]:
        return func(self.value)
