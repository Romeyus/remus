import pytest

from remus import Array, Err, MutArray, Ok


@pytest.fixture
def array() -> Array[int]:
    return Array([1, 1, 2, 3, 3, 4, 5, 5])


def test_count(array: Array[int]):
    assert array.count(1) == 2
    assert array.count(2) == 1
    assert array.count(3) == 2
    assert array.count(4) == 1
    assert array.count(5) == 2
    assert array.count(6) == 0


def test_first(array: Array[int]):
    assert array.first() == 1


def test_last(array: Array[int]):
    assert array.last() == 5


def test__bool__(array: Array[int]):
    assert bool(array) is True
    assert bool(Array[int]([])) is False


def test__contains__(array: Array[int]):
    assert 1 in array
    assert 2 in array
    assert 3 in array
    assert 4 in array
    assert 5 in array
    assert 6 not in array


def test__getitem__(array: Array[int]):
    assert array[0] == Ok(1)
    assert array[1] == Ok(1)
    assert array[2] == Ok(2)
    assert array[3] == Ok(3)
    assert array[4] == Ok(3)
    assert array[5] == Ok(4)
    assert array[6] == Ok(5)
    assert array[7] == Ok(5)
    assert isinstance(array[8], Err) and isinstance(array[8].value, IndexError)


def test__iter__(array: Array[int]):
    assert list(iter(array)) == [1, 1, 2, 3, 3, 4, 5, 5]


def test__len__(array: Array[int]):
    assert len(array) == 8


@pytest.fixture
def mut_array() -> MutArray[int]:
    return MutArray([1, 1, 2, 3, 3, 4, 5, 5])


def test_append(mut_array: MutArray[int]):
    mut_array.append(6)
    assert mut_array[8] == Ok(6)


def test_insert(mut_array: MutArray[int]):
    mut_array.insert(5, 100)
    assert mut_array[5] == Ok(100)


def test_pop(mut_array: MutArray[int]):
    assert mut_array.pop(0) == Ok(1)
    mut_array.pop(0)
    assert mut_array[0] == Ok(2)


def test_pop_or(mut_array: MutArray[int]):
    assert mut_array.pop_or(0, 0) == 1
    assert mut_array.pop_or(100, 1) == 1


def test_prepend(mut_array: MutArray[int]):
    mut_array.prepend(0)
    assert mut_array[0] == Ok(0)


def test__delitem__(mut_array: MutArray[int]):
    del mut_array[0]
    del mut_array[0]
    assert mut_array[0] == Ok(2)


def test__setitem__(mut_array: MutArray[int]):
    mut_array[0] = 2
    assert mut_array[0] == Ok(2)
