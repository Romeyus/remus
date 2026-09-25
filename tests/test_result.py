import pytest

from remus import Err, Ok


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
