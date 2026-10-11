import pytest

from remus import Err, Nothing, Ok, Some, colls, errs


# ==========================================
# ===            Constants                 ===
# ==========================================
@pytest.fixture
def map() -> colls.MutMap[int, str]:
    return colls.MutMap(
        {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday",
        }
    )


# ==========================================
# ===            Map                 ===
# ==========================================
def test_items(map: colls.Map[int, str]) -> None:
    assert list(map.items()) == [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]


def test_keys(map: colls.Map[int, str]) -> None:
    assert list(map.keys()) == [0, 1, 2, 3, 4, 5, 6]


def test_get(map: colls.Map[int, str]) -> None:
    assert map.get(0) == Some("Monday")
    assert map.get(100) == Nothing


def test_get_or(map: colls.Map[int, str]) -> None:
    assert map.get_or(0, "Weekend") == "Monday"
    assert map.get_or(100, "Weekend") == "Weekend"


def test_get_or_else(map: colls.Map[int, str]) -> None:
    assert map.get_or_else(0, lambda: "Weekend") == "Monday"
    assert map.get_or_else(100, lambda: "Weekend") == "Weekend"


def test_values(map: colls.Map[int, str]) -> None:
    assert list(map.values()) == [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]


def test___contains__(map: colls.Map[int, str]) -> None:
    for i in range(7):
        assert i in map

    assert 8 not in map


def test___iter__(map: colls.Map[int, str]) -> None:
    assert list(iter(map)) == [0, 1, 2, 3, 4, 5, 6]


def test___len__(map: colls.Map[int, str]) -> None:
    assert len(map) == 7


# ==========================================
# ===            MutMap                 ===
# ==========================================
def test_clear(map: colls.MutMap[int, str]) -> None:
    map.clear()
    assert map == colls.MutMap()


def test_pop(map: colls.MutMap[int, str]) -> None:
    result = map.pop(2)
    assert 2 not in map
    assert result == Ok("Wednesday")

    result = map.pop(100)
    assert result == Err(errs.KeyErr(100))


def test_pop_or(map: colls.MutMap[int, str]) -> None:
    assert map.pop_or(2, "Funday") == "Wednesday"
    assert map.pop_or(100, "Funday") == "Funday"


def test_pop_or_else(map: colls.MutMap[int, str]) -> None:
    assert map.pop_or_else(2, lambda: "Funday") == "Wednesday"
    assert map.pop_or_else(100, lambda: "Funday") == "Funday"


def test_set(map: colls.MutMap[int, str]) -> None:
    map.set(0, "Another day")
    assert map.get(0) == Some("Another day")

    map.set(100, "Funday")
    assert map.get(100) == Some("Funday")


def test_set_default(map: colls.MutMap[int, str]) -> None:
    value = map.set_default(0, "Another day")
    assert map.get(0) == Some("Monday")
    assert value == "Monday"

    value = map.set_default(100, "Funday")
    assert map.get(100) == Some("Funday")
    assert value == "Funday"


def test_update(map: colls.MutMap[int, str]) -> None:
    map.update({100: "Funday", 101: "Ice cream day"})
    assert map == colls.MutMap(
        {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday",
            100: "Funday",
            101: "Ice cream day",
        }
    )
