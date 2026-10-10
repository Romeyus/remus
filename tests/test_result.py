from unittest import mock

import pytest

from remus import Err, Ok, Result
from remus._internal import Panic


def test_and_() -> None:
    x = Ok(2)
    y = Err("late error")
    assert x.and_(y) == Err("late error")

    x = Err("early error")
    y = Ok("foo")
    assert x.and_(y) == Err("early error")

    x = Err("not a 2")
    y = Err("late error")
    assert x.and_(y) == Err("not a 2")

    x = Ok(2)
    y = Ok("different result type")
    assert x.and_(y) == Ok("different result type")


def test_and_then() -> None:
    def sq_then_to_str(x: int) -> Result[str, str]:
        if x > 1_000_000:
            return Err("overflowed")
        return Ok(str(x**2))

    assert Ok(2).and_then(sq_then_to_str) == Ok("4")
    assert Ok(1_000_001).and_then(sq_then_to_str) == Err("overflowed")
    assert Err("not a number").and_then(sq_then_to_str) == Err("not a number")


def test_expect() -> None:
    assert Ok(2).expect("testing expect") == 2
    with pytest.raises(Panic, match="testing expect: emergency failure"):
        Err("emergency failure").expect("testing expect")


def test_expect_err() -> None:
    assert (
        Err("emergency failure").expect_err("testing expect_err") == "emergency failure"
    )
    with pytest.raises(Panic, match="testing expect_err: 10"):
        Ok(10).expect_err("testing expect_err")


def test_inspect() -> None:
    func = mock.Mock()

    Ok(2).inspect(func)
    func.assert_called_once_with(2)

    func.reset_mock()

    Err("failure").inspect(func)
    func.assert_not_called()


def test_inspect_err() -> None:
    func = mock.Mock()

    Ok(2).inspect_err(func)
    func.assert_not_called()

    func.reset_mock()

    Err("failure").inspect_err(func)
    func.assert_called_once_with("failure")


def test_map() -> None:
    assert Ok(2).map(lambda v: str(v * 2)) == Ok("4")
    assert Err("failure").map(lambda v: str(v * 2)) == Err("failure")


def test_map_err() -> None:
    assert Ok(2).map_err(lambda v: v.upper()) == Ok(2)
    assert Err("failure").map_err(lambda v: v.upper()) == Err("FAILURE")


def test_map_or() -> None:
    assert Ok(2).map_or(lambda v: str(v * 2), "10") == "4"
    assert Err("failure").map_or(lambda v: str(v * 2), "10") == "10"


def test_map_or_else() -> None:
    assert Ok(2).map_or_else(lambda v: str(v * 2), lambda v: v.upper()) == "4"
    assert (
        Err("failure").map_or_else(lambda v: str(v * 2), lambda v: v.upper())
        == "FAILURE"
    )


def test_or_() -> None:
    x = Ok(2)
    y = Err("late error")
    assert x.or_(y) == Ok(2)

    x = Err("early error")
    y = Ok(2)
    assert x.or_(y) == Ok(2)

    x = Err("not a 2")
    y = Err("late error")
    assert x.or_(y) == Err("late error")

    x = Ok(2)
    y = Ok(100)
    assert x.or_(y) == Ok(2)
