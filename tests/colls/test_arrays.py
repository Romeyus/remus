import pytest

from remus import Err, Ok, colls

ARRAY_LENGTH = 10


@pytest.fixture
def array() -> colls.MutArray[int]:
    return colls.MutArray([i for i in range(ARRAY_LENGTH)])


def test___getitem__(array: colls.Array[int]):
    for i in range(ARRAY_LENGTH):
        assert array[i] == Ok(i)

    assert array[ARRAY_LENGTH + 1] == Err(colls.IndexErr(ARRAY_LENGTH + 1))
