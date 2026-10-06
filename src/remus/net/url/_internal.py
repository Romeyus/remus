from typing import Self


# ==========================================
# ===            Path                 ===
# ==========================================
class Path(str):
    def __new__(cls, value: str) -> Self:
        parts = [p for p in value.split("/") if p]
        normalised = "/".join(parts)
        return super().__new__(cls, f"/{normalised}")
