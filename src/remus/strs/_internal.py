from typing import Self


class Lowercase(str):
    def __new__(cls, value: str) -> Self:
        return super().__new__(cls, value.lower())
