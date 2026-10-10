from unittest import mock

import pytest

from remus import Maybe, Nothing, Some
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
