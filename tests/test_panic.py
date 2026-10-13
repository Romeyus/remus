import pytest

from remus import panic
from remus._internal import Panic


def test_panic_raises_Panic_with_message() -> None:
    with pytest.raises(Panic, match="Something went wrong."):
        panic("Something went wrong.")
