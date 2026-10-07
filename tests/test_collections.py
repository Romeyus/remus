import pytest

from remus import (
    Array,
    Err,
    Map,
    MutArray,
    MutMap,
    Nothing,
    Ok,
    Some,
    new_array,
    new_map,
    new_mut_array,
    new_mut_map,
)


# ==========================================
# ===            Array                 ===
# ==========================================
class TestArray:
    @pytest.fixture
    def array(self) -> Array[int]:
        return new_array([i for i in range(10)])

    def test_count(self, array: Array[int]):
        assert array.count(0) == 1
        assert array.count(9) == 1
        assert array.count(10) == 0

    def test_first(self, array: Array[int]):
        assert array.first() == Some(0)
        assert new_array().first() == Nothing

    def test_first_or(self, array: Array[int]):
        assert array.first_or(10) == 0
        assert new_array().first_or(10) == 10

    def test_get(self, array: Array[int]):
        assert array.get(0) == Some(0)
        assert array.get(9) == Some(9)
        assert array.get(10) == Nothing

    def test_get_or(self, array: Array[int]):
        assert array.get_or(0, 10) == 0
        assert array.get_or(9, 10) == 9
        assert array.get_or(10, 10) == 10

    def test_last(self, array: Array[int]):
        assert array.last() == Some(9)
        assert new_array().last() == Nothing

    def test_last_or(self, array: Array[int]):
        assert array.last_or(10) == 9
        assert new_array().last_or(10) == 10

    def test__contains__(self, array: Array[int]):
        assert 0 in array
        assert 9 in array
        assert 10 not in array

    def test__getitem__(self, array: Array[int]):
        assert array[0] == Ok(0)
        assert array[9] == Ok(9)
        assert isinstance(array[10], Err) and isinstance(array[10].value, IndexError)

    def test__iter__(self, array: Array[int]):
        assert list(iter(array)) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test__len__(self, array: Array[int]):
        assert len(array) == 10


class TestMutArray:
    @pytest.fixture
    def mut_array(self) -> MutArray[int]:
        return new_mut_array([i for i in range(10)])

    def test_append(self, mut_array: MutArray[int]):
        mut_array.append(10)
        assert mut_array.last() == Some(10)

    def test_insert(self, mut_array: MutArray[int]):
        mut_array.insert(5, 10)
        assert mut_array.get(5) == Some(10)

    def test_pop(self, mut_array: MutArray[int]):
        assert mut_array.pop(5) == Ok(5)
        assert mut_array.last() == Some(9)

    def test_pop_or(self, mut_array: MutArray[int]):
        assert mut_array.pop_or(5, 10) == 5
        assert mut_array.pop_or(100, 0) == 0

    def test_pop_or_else(self, mut_array: MutArray[int]):
        assert mut_array.pop_or_else(5, lambda: 10) == 5
        assert mut_array.pop_or_else(100, lambda: 0) == 0

    def test_prepend(self, mut_array: MutArray[int]):
        mut_array.prepend(10)
        assert mut_array.first() == Some(10)

    def test__delitem__(self, mut_array: MutArray[int]):
        del mut_array[5]
        assert 5 not in mut_array

    def test__setitem__(self, mut_array: MutArray[int]):
        mut_array[5] = 10
        assert mut_array.get(5) == Some(10)


# ==========================================
# ===            Map                 ===
# ==========================================
class TestMap:
    @pytest.fixture
    def map(self) -> Map[str, int]:
        return new_map(
            {
                "one": 1,
                "two": 2,
                "three": 3,
                "four": 4,
                "five": 5,
            }
        )

    def test_get(self, map: Map[str, int]):
        assert map.get("one") == Some(1)
        assert map.get("two") == Some(2)
        assert map.get("three") == Some(3)
        assert map.get("four") == Some(4)
        assert map.get("five") == Some(5)
        assert map.get("six") == Nothing

    def test_get_or(self, map: Map[str, int]):
        assert map.get_or("one", 0) == 1
        assert map.get_or("two", 0) == 2
        assert map.get_or("three", 0) == 3
        assert map.get_or("four", 0) == 4
        assert map.get_or("five", 0) == 5
        assert map.get_or("six", 0) == 0

    def test_get_or_else(self, map: Map[str, int]):
        assert map.get_or_else("one", lambda: 0) == 1
        assert map.get_or_else("two", lambda: 0) == 2
        assert map.get_or_else("three", lambda: 0) == 3
        assert map.get_or_else("four", lambda: 0) == 4
        assert map.get_or_else("five", lambda: 0) == 5
        assert map.get_or_else("six", lambda: 0) == 0

    def test_items(self, map: Map[str, int]):
        assert list(map.items()) == [
            ("one", 1),
            ("two", 2),
            ("three", 3),
            ("four", 4),
            ("five", 5),
        ]

    def test_keys(self, map: Map[str, int]):
        assert list(map.keys()) == ["one", "two", "three", "four", "five"]

    def test_values(self, map: Map[str, int]):
        assert list(map.values()) == [1, 2, 3, 4, 5]

    def test__contains__(self, map: Map[str, int]):
        assert "one" in map
        assert "two" in map
        assert "three" in map
        assert "four" in map
        assert "five" in map
        assert "six" not in map

    def test__getitem__(self, map: Map[str, int]):
        assert map["one"] == Ok(1)
        assert map["two"] == Ok(2)
        assert map["three"] == Ok(3)
        assert map["four"] == Ok(4)
        assert map["five"] == Ok(5)
        assert isinstance(map["six"], Err) and isinstance(map["six"].value, KeyError)

    def test__iter__(self, map: Map[str, int]):
        assert list(iter(map)) == ["one", "two", "three", "four", "five"]

    def test__len__(self, map: Map[str, int]):
        assert len(map) == 5


class TestMutMap:
    @pytest.fixture
    def mut_map(self) -> MutMap[str, int]:
        return new_mut_map(
            {
                "one": 1,
                "two": 2,
                "three": 3,
                "four": 4,
                "five": 5,
            }
        )

    def test_insert(self, mut_map: MutMap[str, int]):
        assert mut_map.insert("six", 6) == Nothing
        assert mut_map["six"] == Ok(6)
        assert mut_map.insert("one", 10) == Some(1)
        assert mut_map["one"] == Ok(1)

    def test_insert_or(self, mut_map: MutMap[str, int]):
        assert mut_map.insert_or("six", 6) == 6
        assert mut_map["six"] == Ok(6)
        assert mut_map.insert_or("one", 10) == 1
        assert mut_map["one"] == Ok(1)

    def test_pop(self, mut_map: MutMap[str, int]):
        assert mut_map.pop("one") == Ok(1)
        assert mut_map.get("one") == Nothing
        assert isinstance(mut_map.pop("six"), Err) and isinstance(
            mut_map.pop("six").value, KeyError
        )

    def test_pop_or(self, mut_map: MutMap[str, int]):
        assert mut_map.pop_or("one", 10) == 1
        assert mut_map.get("one") == Nothing
        assert mut_map.pop_or("six", 10) == 10

    def test_pop_or_else(self, mut_map: MutMap[str, int]):
        assert mut_map.pop_or_else("one", lambda: 10) == 1
        assert mut_map.get("one") == Nothing
        assert mut_map.pop_or_else("six", lambda: 10) == 10

    def test__delitem__(self, mut_map: MutMap[str, int]):
        del mut_map["one"]
        assert mut_map.get("one") == Nothing

    def test__setitem__(self, mut_map: MutMap[str, int]):
        mut_map["one"] = 10
        assert mut_map.get("one") == Some(10)
