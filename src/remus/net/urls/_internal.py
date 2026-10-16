from dataclasses import dataclass

from remus import panic


# ==========================================
# ===            Routing                 ===
# ==========================================
@dataclass(frozen=True, slots=True)
class Path:
    value: str

    def __post_init__(self) -> None:
        if ".." in self.value:
            panic(
                f"path contains '..', navigating to parent directories is forbidden, {self.value}"
            )

        parts = [p for p in self.value.split("/") if p]
        normalised = "/".join(parts)
        object.__setattr__(self, "value", f"/{normalised}")
