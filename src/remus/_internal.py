import sys
from dataclasses import dataclass
from threading import current_thread
from traceback import extract_tb, print_tb
from types import TracebackType
from typing import Never

# ==========================================
# ===            Constants                 ===
# ==========================================
_PANIC_FONT_RED_BOLD = "\x1b[1;31m"
_PANIC_FONT_RESET = "\x1b[0m"


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
