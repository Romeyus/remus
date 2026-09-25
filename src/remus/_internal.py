from abc import ABC, abstractmethod
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


@dataclass(frozen=True, slots=True)
class Ok[T, E = Any](_BaseResult[T, E]):
    value: T

    def and_[U](self, result: Result[U, E]) -> Result[U, E]:
        return result


@dataclass(frozen=True, slots=True)
class Err[E, T = Any](_BaseResult[T, E]):
    value: E

    def and_[U](self, result: Result[U, E]) -> Result[U, E]:
        return cast(Result[U, E], self)
