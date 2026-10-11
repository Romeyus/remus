import pytest

from remus import Err, Nothing, Ok, Some, colls
from remus._internal import Panic

# ==========================================
# ===            Constants                 ===
# ==========================================
ARRAY_LENGTH = 10


@pytest.fixture
def array() -> colls.MutArray[int]:
    return colls.MutArray([i for i in range(ARRAY_LENGTH)])


# ==========================================
# ===            Array                 ===
# ==========================================
def test_count(array: colls.BaseArray[int]) -> None:
    for i in range(ARRAY_LENGTH):
        assert array.count(i) == 1

    assert array.count(ARRAY_LENGTH + 1) == 0
    assert colls.Array([100] * 10).count(100) == 10


def test_get(array: colls.BaseArray[int]) -> None:
    for i in range(ARRAY_LENGTH):
        assert array.get(i) == Some(i)

    assert array.get(ARRAY_LENGTH + 1) == Nothing


def test_get_or(array: colls.BaseArray[int]) -> None:
    for i in range(ARRAY_LENGTH):
        assert array.get_or(i, 100) == i

    assert array.get_or(ARRAY_LENGTH + 1, 100) == 100


def test_get_or_else(array: colls.BaseArray[int]) -> None:
    for i in range(ARRAY_LENGTH):
        assert array.get_or_else(i, lambda: 100) == i

    assert array.get_or_else(ARRAY_LENGTH + 1, lambda: 100) == 100


def test___contains__(array: colls.Array[int]) -> None:
    for i in range(ARRAY_LENGTH):
        assert i in array

    assert (ARRAY_LENGTH + 1) not in array


def test___getitem__(array: colls.Array[int]) -> None:
    for i in range(ARRAY_LENGTH):
        assert array[i] == Ok(i)

    assert array[ARRAY_LENGTH + 1] == Err(colls.IndexErr(ARRAY_LENGTH + 1))


def test___iter__(array: colls.Array[int]) -> None:
    assert list(iter(array)) == [i for i in range(ARRAY_LENGTH)]


def test___len__(array: colls.Array[int]) -> None:
    assert len(array) == ARRAY_LENGTH


# ==========================================
# ===            MutArray                 ===
# ==========================================
def test_append(array: colls.BaseMutArray[int]) -> None:
    array.append(100)
    assert array[-1] == Ok(100)
    assert len(array) == ARRAY_LENGTH + 1


def test_insert(array: colls.MutArray[int]) -> None:
    array.insert(0, 100)
    assert array[0] == Ok(100)

    array.insert(5, 200)
    assert array[5] == Ok(200)

    array.insert(len(array), 300)
    assert array[-1] == Ok(300)


def test___delitem__(array: colls.MutArray[int]) -> None:
    del array[5]
    assert len(array) == ARRAY_LENGTH - 1
    assert 5 not in array

    with pytest.raises(Panic):
        del array[ARRAY_LENGTH + 1]


def test___setitem__(array: colls.MutArray[int]) -> None:
    array[5] = 100
    assert array[5] == Ok(100)

    with pytest.raises(Panic):
        array[ARRAY_LENGTH + 1] = 200
