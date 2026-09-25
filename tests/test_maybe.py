from unittest import mock

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


def test_and_then(some: Some[int]) -> None:
    def func(value: int) -> Some[int]:
        return Some(value + 1)

    assert some.and_then(func) == Some(2)
    assert Nothing.and_then(func) == Nothing


def test_filter(some: Some[int]) -> None:
    def is_even(value: int) -> bool:
        return value % 2 == 0

    def is_odd(value: int) -> bool:
        return not is_even(value)

    assert some.filter(is_even) == Nothing
    assert Nothing.filter(is_even) == Nothing

    assert some.filter(is_odd) == some
    assert Nothing.filter(is_odd) == Nothing


def test_inspect(some: Some[int]) -> None:
    func = mock.Mock()

    assert some.inspect(func) == some
    func.assert_called_once_with(1)

    func.reset_mock()

    assert Nothing.inspect(func) == Nothing
    func.assert_not_called()


def test_map(some: Some[int]) -> None:
    def func(value: int) -> int:
        return value * 2

    assert some.map(func) == Some(2)
    assert Nothing.map(func) == Nothing


def test_map_or(some: Some[int]) -> None:
    def func(value: int) -> int:
        return value * 2

    assert some.map_or(func, 0) == 2
    assert Nothing.map_or(func, 0) == 0


def test_map_or_else(some: Some[int]) -> None:
    def func(value: int) -> int:
        return value * 2

    assert some.map_or_else(func, lambda: 0) == 2
    assert Nothing.map_or_else(func, lambda: 0) == 0


def test_ok_or(some: Some[int]) -> None:
    err_value = "something went wrong"

    assert some.ok_or(err_value) == Ok(1)
    assert Nothing.ok_or(err_value) == Err(err_value)


def test_ok_or_else(some: Some[int]) -> None:
    def func() -> str:
        return "something went wrong"

    assert some.ok_or_else(func) == Ok(1)
    assert Nothing.ok_or_else(func) == Err("something went wrong")


def test_or_(some: Some[int]) -> None:
    some_maybe = Some(2)

    assert some.or_(some_maybe) == some
    assert some.or_(Nothing) == some

    assert Nothing.or_(some_maybe) == some_maybe
    assert Nothing.or_(Nothing) == Nothing


def test_or_else(some: Some[int]) -> None:
    def func() -> Some[int]:
        return Some(2)

    assert some.or_else(func) == some
    assert Nothing.or_else(func) == Some(2)


def test_unwrap(some: Some[int]) -> None:
    assert some.unwrap() == 1
    with pytest.raises(Panic):
        Nothing.unwrap()


def test_unwrap_or(some: Some[int]) -> None:
    assert some.unwrap_or(2) == 1
    assert Nothing.unwrap_or(2) == 2
