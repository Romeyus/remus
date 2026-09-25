import pytest

from remus import Err, Map, Nothing, Ok, Some


@pytest.fixture
def map() -> Map[int, str]:
    return Map(
        {
            0: "zero",
            1: "one",
            2: "two",
        }
    )


def test_get(map: Map[int, str]) -> None:
    assert map.get(0) == Some("zero")
    assert map.get(1) == Some("one")
    assert map.get(2) == Some("two")
    assert map.get(3) == Nothing


def test_get_or(map: Map[int, str]) -> None:
    assert map.get_or(0, "default") == "zero"
    assert map.get_or(1, "default") == "one"
    assert map.get_or(2, "default") == "two"
    assert map.get_or(3, "default") == "default"


def test_items(map: Map[int, str]) -> None:
    assert list(map.items()) == [(0, "zero"), (1, "one"), (2, "two")]


def test_keys(map: Map[int, str]) -> None:
    assert list(map.keys()) == [0, 1, 2]


def test_values(map: Map[int, str]) -> None:
    assert list(map.values()) == ["zero", "one", "two"]


def test__contains__(map: Map[int, str]) -> None:
    assert 0 in map
    assert 1 in map
    assert 2 in map
    assert 3 not in map


def test__getitem__(map: Map[int, str]) -> None:
    assert map[0] == Ok("zero")
    assert map[1] == Ok("one")
    assert map[2] == Ok("two")
    assert isinstance(map[3], Err) and isinstance(map[3].value, KeyError)


def test__iter__(map: Map[int, str]) -> None:
    for i in map:
        assert i in [0, 1, 2]

    assert 3 not in map


def test__len__(map: Map[int, str]) -> None:
    assert len(map) == 3
