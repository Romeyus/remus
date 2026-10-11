from abc import ABC
from collections.abc import MutableSequence, Sequence
from dataclasses import dataclass


# ==========================================
# ===            Arrays                 ===
# ==========================================
class BaseArray[T](ABC): ...


@dataclass(frozen=True, slots=True)
class Array[T](BaseArray[T]):
    data: Sequence[T]


@dataclass(frozen=True, slots=True)
class MutArray[T](Array[T], BaseArray[T]):
    data: MutableSequence[T]
