from unittest import mock

import pytest

from remus import Err, Maybe, Nothing, Ok, Some
from remus._internal import Panic


def test_and_() -> None:
    x = Some(2)
    y = Nothing
    assert x.and_(y) == Nothing

    x = Nothing
    y = Some("foo")
    assert x.and_(y) == Nothing

    x = Some(2)
    y = Some("foo")
    assert x.and_(y) == Some("foo")

    x = Nothing
    y = Nothing
    assert x.and_(y) == Nothing


def test_and_then() -> None:
    def sq_then_to_str(x: int) -> Maybe[str]:
        if x > 1_000_000:
            return Nothing
        return Some(str(x**2))

    assert Some(2).and_then(sq_then_to_str) == Some("4")
    assert Some(1_000_001).and_then(sq_then_to_str) == Nothing  # overflowed
    assert Nothing.and_then(sq_then_to_str) == Nothing


def test_expect() -> None:
    assert Some(2).expect("testing expect") == 2
    with pytest.raises(Panic, match="testing expect"):
        Nothing.expect("testing expect")


def test_filter() -> None:
    def is_even(x: int) -> bool:
        return x % 2 == 0

    assert Nothing.filter(is_even) == Nothing
    assert Some(3).filter(is_even) == Nothing
    assert Some(4).filter(is_even) == Some(4)


def test_inspect() -> None:
    func = mock.Mock()

    func = mock.Mock()

    Some(2).inspect(func)
    func.assert_called_once_with(2)

    func.reset_mock()

    Nothing.inspect(func)
    func.assert_not_called()


def test_map() -> None:
    assert Some("Hello world!").map(lambda v: len(v)) == Some(12)
    assert Nothing.map(lambda v: len(v)) == Nothing


def test_map_or() -> None:
    assert Some("foo").map_or(lambda v: len(v), 42) == 3
    assert Nothing.map_or(lambda v: len(v), 42) == 42


def test_map_or_else() -> None:
    assert Some("foo").map_or_else(lambda v: len(v), lambda: 2 * 21) == 3
    assert Nothing.map_or_else(lambda v: len(v), lambda: 2 * 21) == 42


def test_ok_or() -> None:
    assert Some("foo").ok_or(0) == Ok("foo")
    assert Nothing.ok_or(0) == Err(0)


def test_ok_or_else() -> None:
    assert Some("foo").ok_or_else(lambda: 0) == Ok("foo")
    assert Nothing.ok_or_else(lambda: 0) == Err(0)


def test_or_() -> None:
    x = Some(2)
    y = Nothing
    assert x.or_(y) == Some(2)

    x = Nothing
    y = Some(100)
    assert x.or_(y) == Some(100)

    x = Some(2)
    y = Some(100)
    assert x.or_(y) == Some(2)

    x = Nothing
    y = Nothing
    assert x.or_(y) == Nothing


def test_or_else() -> None:
    def nobody() -> Maybe[str]:
        return Nothing

    def vikings() -> Maybe[str]:
        return Some("vikings")

    assert Some("barbarians").or_else(vikings) == Some("barbarians")
    assert Nothing.or_else(vikings) == Some("vikings")
    assert Nothing.or_else(nobody) == Nothing


def test_unwrap() -> None:
    assert Some("air").unwrap() == "air"
    with pytest.raises(Panic):
        Nothing.unwrap()


def test_unwrap_or() -> None:
    assert Some("car").unwrap_or("bike") == "car"
    assert Nothing.unwrap_or("bike") == "bike"


def test_unwrap_or_else() -> None:
    assert Some(4).unwrap_or_else(lambda: 2 * 10) == 4
    assert Nothing.unwrap_or_else(lambda: 2 * 10) == 20
