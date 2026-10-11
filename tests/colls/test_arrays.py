import pytest

from remus import Err, Nothing, Ok, Some, colls, errs

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
def test_count(array: colls.Array[int]) -> None:
    for i in range(ARRAY_LENGTH):
        assert array.count(i) == 1

    assert array.count(ARRAY_LENGTH + 1) == 0
    assert colls.Array([100] * 10).count(100) == 10


def test_first(array: colls.Array[int]) -> None:
    assert array.first() == Some(0)
    assert colls.Array().first() == Nothing


def test_get(array: colls.Array[int]) -> None:
    for i in range(ARRAY_LENGTH):
        assert array.get(i) == Some(i)

    assert array.get(ARRAY_LENGTH + 1) == Nothing


def test_get_or(array: colls.Array[int]) -> None:
    for i in range(ARRAY_LENGTH):
        assert array.get_or(i, 100) == i

    assert array.get_or(ARRAY_LENGTH + 1, 100) == 100


def test_get_or_else(array: colls.Array[int]) -> None:
    for i in range(ARRAY_LENGTH):
        assert array.get_or_else(i, lambda: 100) == i

    assert array.get_or_else(ARRAY_LENGTH + 1, lambda: 100) == 100


def test_index(array: colls.Array[int]) -> None:
    for i in range(ARRAY_LENGTH):
        assert array.index(i) == Some(i)

    assert array.index(ARRAY_LENGTH + 1) == Nothing


def test_last(array: colls.Array[int]) -> None:
    assert array.last() == Some(ARRAY_LENGTH - 1)
    assert colls.Array().last() == Nothing


def test___contains__(array: colls.Array[int]) -> None:
    for i in range(ARRAY_LENGTH):
        assert i in array

    assert (ARRAY_LENGTH + 1) not in array


def test___iter__(array: colls.Array[int]) -> None:
    assert list(iter(array)) == [i for i in range(ARRAY_LENGTH)]


def test___len__(array: colls.Array[int]) -> None:
    assert len(array) == ARRAY_LENGTH


# ==========================================
# ===            MutArray                 ===
# ==========================================
def test_append(array: colls.MutArray[int]) -> None:
    array.append(100)
    assert array.get(-1) == Some(100)
    assert len(array) == ARRAY_LENGTH + 1


def test_clear(array: colls.MutArray[int]) -> None:
    array.clear()
    for i in range(ARRAY_LENGTH):
        assert i not in array

    array = colls.MutArray()
    array.clear()
    assert array == colls.MutArray()


def test_extend(array: colls.MutArray[int]) -> None:
    array.extend([100, 200, 300])
    assert array.get(-1) == Some(300)
    assert array.get(-2) == Some(200)
    assert array.get(-3) == Some(100)


def test_insert(array: colls.MutArray[int]) -> None:
    array.insert(0, 100)
    assert array.get(0) == Some(100)

    array.insert(5, 200)
    assert array.get(5) == Some(200)

    array.insert(len(array), 300)
    assert array.get(-1) == Some(300)


def test_prepend(array: colls.MutArray[int]) -> None:
    array.prepend(100)
    assert array.get(0) == Some(100)
    assert len(array) == ARRAY_LENGTH + 1


def test_pop(array: colls.MutArray[int]) -> None:
    assert array.pop(5) == Ok(5)
    assert 5 not in array
    assert len(array) == ARRAY_LENGTH - 1

    assert array.pop(ARRAY_LENGTH + 1) == Err(errs.IndexErr(ARRAY_LENGTH + 1))


def test_pop_or(array: colls.MutArray[int]) -> None:
    assert array.pop_or(5, 100) == 5
    assert array.pop_or(ARRAY_LENGTH + 1, 100) == 100


def test_pop_or_else(array: colls.MutArray[int]) -> None:
    assert array.pop_or_else(5, lambda: 100) == 5
    assert array.pop_or_else(ARRAY_LENGTH + 1, lambda: 100) == 100


def test_remove() -> None:
    array = colls.MutArray([1, 2, 2, 3, 3, 3])
    result = array.remove(3)
    assert array == colls.MutArray([1, 2, 2, 3, 3])
    assert result.value is None

    result = array.remove(4)
    assert array == colls.MutArray([1, 2, 2, 3, 3])
    assert isinstance(result.value, errs.ValueErr)


def test_set(array: colls.MutArray[int]) -> None:
    result = array.set(0, 100)
    assert array.get(0) == Some(100)
    assert result.value is None

    result = array.set(ARRAY_LENGTH + 1, 200)
    assert result.value == errs.IndexErr(ARRAY_LENGTH + 1)
