import pytest

from remus import Array, Err, Ok


@pytest.fixture
def array():
    return Array([1, 1, 2, 3, 3, 4, 5, 5])


def test_count(array: Array[int]):
    assert array.count(1) == 2
    assert array.count(2) == 1
    assert array.count(3) == 2
    assert array.count(4) == 1
    assert array.count(5) == 2
    assert array.count(6) == 0


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
