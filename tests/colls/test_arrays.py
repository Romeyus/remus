import pytest

from remus import Err, Ok, colls

ARRAY_LENGTH = 10


@pytest.fixture
def array() -> colls.MutArray[int]:
    return colls.MutArray([i for i in range(ARRAY_LENGTH)])


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
