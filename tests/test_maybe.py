import pytest

from remus import Err, Nothing, Ok, Panic, Some


@pytest.fixture
def some() -> Some[int]:
    return Some(1)


def test_and_(some: Some[int]) -> None:
    some_maybe = Some(2)

    assert some.and_(some_maybe) == some_maybe
    assert some.and_(Nothing) == Nothing

    assert Nothing.and_(some_maybe) == Nothing
    assert Nothing.and_(Nothing) == Nothing


def test_ok_or(some: Some[int]) -> None:
    err_value = "something went wrong"

    assert some.ok_or(err_value) == Ok(1)
    assert Nothing.ok_or(err_value) == Err(err_value)


def test_or_(some: Some[int]) -> None:
    some_maybe = Some(2)

    assert some.or_(some_maybe) == some
    assert some.or_(Nothing) == some

    assert Nothing.or_(some_maybe) == some_maybe
    assert Nothing.or_(Nothing) == Nothing


def test_unwrap(some: Some[int]) -> None:
    assert some.unwrap() == 1
    with pytest.raises(Panic):
        Nothing.unwrap()
