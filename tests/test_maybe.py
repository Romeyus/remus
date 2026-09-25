import pytest

from remus import Nothing, Some


@pytest.fixture
def some() -> Some[int]:
    return Some(1)


def test_and_(some: Some[int]) -> None:
    some_maybe = Some(2)

    assert some.and_(some_maybe) == some_maybe
    assert some.and_(Nothing) == Nothing

    assert Nothing.and_(some_maybe) == Nothing
    assert Nothing.and_(Nothing) == Nothing
