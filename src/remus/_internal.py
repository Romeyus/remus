from abc import ABC
from dataclasses import dataclass
from typing import Any

# ==========================================
# ===            Result                 ===
# ==========================================
type Result[T, E] = Ok[T, E] | Err[E, T]


class _BaseResult[T, E](ABC): ...


@dataclass(frozen=True, slots=True)
class Ok[T, E = Any](_BaseResult[T, E]):
    value: T


@dataclass(frozen=True, slots=True)
class Err[E, T = Any](_BaseResult[T, E]):
    value: E
