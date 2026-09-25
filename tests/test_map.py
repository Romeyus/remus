import pytest

from remus import Err, Map, Ok


@pytest.fixture
def map() -> Map[int, str]:
    return Map(
        {
            0: "zero",
            1: "one",
            2: "two",
        }
    )


def test__getitem__(map: Map[int, str]) -> None:
    assert map[0] == Ok("zero")
    assert map[1] == Ok("one")
    assert map[2] == Ok("two")
    assert isinstance(map[3], Err) and isinstance(map[3].value, KeyError)
