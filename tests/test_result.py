import pytest

from remus import Err, Nothing, Ok, Panic, Some


@pytest.fixture
def ok() -> Ok[int]:
    return Ok(1)


@pytest.fixture
def err() -> Err[str]:
    return Err("something went wrong")


def test_and_(ok: Ok[int], err: Err[str]) -> None:
    ok_res = Ok(2)
    err_res = Err("something else went wrong")

    assert ok.and_(ok_res) == ok_res
    assert ok.and_(err_res) == err_res

    assert err.and_(ok_res) == err
    assert err.and_(err_res) == err


def test_and_then(ok: Ok[int], err: Err[str]) -> None:
    def func(value: int) -> Ok[int]:
        return Ok(value + 1)

    assert ok.and_then(func) == Ok(2)
    assert err.and_then(func) == err


def test_map(ok: Ok[int], err: Err[str]) -> None:
    def func(value: int) -> int:
        return value + 1

    assert ok.map(func) == Ok(2)
    assert err.map(func) == err


def test_map_err(ok: Ok[int], err: Err[str]) -> None:
    def func(value: str) -> str:
        return value.upper()

    assert ok.map_err(func) == ok
    assert err.map_err(func) == Err("SOMETHING WENT WRONG")


def test_map_or(ok: Ok[int], err: Err[str]) -> None:
    def func(value: int) -> int:
        return value + 1

    assert ok.map_or(func, 0) == 2
    assert err.map_or(func, 0) == 0


def test_map_or_else(ok: Ok[int], err: Err[str]) -> None:
    def func(value: int) -> int:
        return value + 1

    assert ok.map_or_else(func, lambda _: 0) == 2
    assert err.map_or_else(func, lambda _: 0) == 0


def test_ok(ok: Ok[int], err: Err[str]) -> None:
    assert ok.ok() == Some(1)
    assert err.ok() == Nothing


def test_or_(ok: Ok[int], err: Err[str]) -> None:
    ok_res = Ok(2)
    err_res = Err("something else went wrong")

    assert ok.or_(ok_res) == ok
    assert ok.or_(err_res) == ok

    assert err.or_(ok_res) == ok_res
    assert err.or_(err_res) == err_res


def test_or_else(ok: Ok[int], err: Err[str]) -> None:
    def func(value: str) -> Err[str]:
        return Err("something else went wrong")

    assert ok.or_else(func) == ok
    assert err.or_else(func) == Err("something else went wrong")


def test_unwrap(ok: Ok[int], err: Err[str]) -> None:
    assert ok.unwrap() == 1
    with pytest.raises(Panic):
        err.unwrap()


def test_unwrap_err(ok: Ok[int], err: Err[str]) -> None:
    with pytest.raises(Panic):
        ok.unwrap_err()
    assert err.unwrap_err() == "something went wrong"


def test_unwrap_or(ok: Ok[int], err: Err[str]) -> None:
    assert ok.unwrap_or(2) == 1
    assert err.unwrap_or(2) == 2


def test_unwrap_or_else(ok: Ok[int], err: Err[str]) -> None:
    def func(value: str) -> int:
        return 2

    assert ok.unwrap_or_else(func) == 1
    assert err.unwrap_or_else(func) == 2
