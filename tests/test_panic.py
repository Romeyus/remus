import pytest

from remus import panic
from remus._internal import Panic


def test_panic_should_raise_panic_with_message() -> None:
    with pytest.raises(Panic, match="testing panic"):
        panic("testing panic")
