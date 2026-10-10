from dataclasses import dataclass
from typing import Never


# ==========================================
# ===            Panic                 ===
# ==========================================
@dataclass(frozen=True, slots=True)
class Panic(BaseException):
    message: str


def panic(message: str) -> Never:
    raise Panic(message)
