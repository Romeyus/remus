from unittest import mock

import pytest

from remus import Err, Nothing, Ok, Panic, Some


# ==========================================
# ===            Maybe                 ===
# ==========================================
class TestSome:
    @pytest.fixture
    def some(self) -> Some[int]:
        return Some(100)

    def test_and_(self, some: Some[int]) -> None:
        assert some.and_(Some(200)) == Some(200)

    def test_and_then(self, some: Some[int]) -> None:
        assert some.and_then(lambda x: Some(x * 2)) == Some(200)

    def test_filter(self, some: Some[int]) -> None:
        assert some.filter(lambda _: True) == Some(100)
        assert some.filter(lambda _: False) == Nothing

    def test_inspect(self, some: Some[int]) -> None:
        func = mock.Mock()
        some.inspect(func)
        func.assert_called_once_with(100)

    def test_map(self, some: Some[int]) -> None:
        assert some.map(lambda x: x * 2) == Some(200)

    def test_ok_or(self, some: Some[int]) -> None:
        assert some.ok_or("An error has occurred.") == Ok(100)

    def test_ok_or_else(self, some: Some[int]) -> None:
        assert some.ok_or_else(lambda: "An error has occurred.") == Ok(100)

    def test_or_(self, some: Some[int]) -> None:
        assert some.or_(Nothing) == some

    def test_or_else(self, some: Some[int]) -> None:
        assert some.or_else(lambda: Nothing) == some

    def test_unwrap(self, some: Some[int]) -> None:
        assert some.unwrap() == 100

    def test_unwrap_or(self, some: Some[int]) -> None:
        assert some.unwrap_or(0) == 100

    def test_unwrap_or_else(self, some: Some[int]) -> None:
        assert some.unwrap_or_else(lambda: 0) == 100


class TestNothing:
    def test_and_(self) -> None:
        assert Nothing.and_(Some(100)) == Nothing

    def test_and_then(self) -> None:
        assert Nothing.and_then(lambda x: Some(x * 2)) == Nothing

    def test_filter(self) -> None:
        assert Nothing.filter(lambda _: True) == Nothing
        assert Nothing.filter(lambda _: False) == Nothing

    def test_inspect(self) -> None:
        func = mock.Mock()
        Nothing.inspect(func)
        func.assert_not_called()

    def test_map(self) -> None:
        assert Nothing.map(lambda x: x * 2) == Nothing

    def test_ok_or(self) -> None:
        assert Nothing.ok_or("An error has occurred.") == Err("An error has occurred.")

    def test_ok_or_else(self) -> None:
        assert Nothing.ok_or_else(lambda: "An error has occurred.") == Err(
            "An error has occurred."
        )

    def test_or_(self) -> None:
        assert Nothing.or_(Some(100)) == Some(100)

    def test_or_else(self) -> None:
        assert Nothing.or_else(lambda: Some(100)) == Some(100)

    def test_unwrap(self) -> None:
        with pytest.raises(Panic):
            Nothing.unwrap()

    def test_unwrap_or(self) -> None:
        assert Nothing.unwrap_or(0) == 0

    def test_unwrap_or_else(self) -> None:
        assert Nothing.unwrap_or_else(lambda: 0) == 0


# ==========================================
# ===            Result                 ===
# ==========================================
class TestOk:
    @pytest.fixture
    def ok(self) -> Ok[int]:
        return Ok(100)

    def test_and_(self, ok: Ok[int]) -> None:
        assert ok.and_(Ok(200)) == Ok(200)

    def test_and_then(self, ok: Ok[int]) -> None:
        assert ok.and_then(lambda x: Ok(x * 2)) == Ok(200)

    def test_err(self, ok: Ok[int]) -> None:
        assert ok.err() == Nothing

    def test_inspect(self, ok: Ok[int]) -> None:
        func = mock.Mock()
        ok.inspect(func)
        func.assert_called_once_with(100)

    def test_inspect_err(self, ok: Ok[int]) -> None:
        func = mock.Mock()
        ok.inspect_err(func)
        func.assert_not_called()

    def test_map(self, ok: Ok[int]) -> None:
        assert ok.map(lambda x: x * 2) == Ok(200)

    def test_map_err(self, ok: Ok[int]) -> None:
        assert ok.map_err(lambda _: "An error has occurred.") == Ok(100)

    def test_map_or(self, ok: Ok[int]) -> None:
        assert ok.map_or(lambda x: x * 2, 0) == 200

    def test_map_or_else(self, ok: Ok[int]) -> None:
        assert ok.map_or_else(lambda x: x * 2, lambda _: 0) == 200

    def test_ok(self, ok: Ok[int]) -> None:
        assert ok.ok() == Some(100)

    def test_or_(self, ok: Ok[int]) -> None:
        assert ok.or_(Ok(200)) == Ok(100)

    def test_or_else(self, ok: Ok[int]) -> None:
        assert ok.or_else(lambda _: Ok(200)) == Ok(100)

    def test_unwrap(self, ok: Ok[int]) -> None:
        assert ok.unwrap() == 100

    def test_unwrap_err(self, ok: Ok[int]) -> None:
        with pytest.raises(Panic):
            ok.unwrap_err()

    def test_unwrap_or(self, ok: Ok[int]) -> None:
        assert ok.unwrap_or(0) == 100

    def test_unwrap_or_else(self, ok: Ok[int]) -> None:
        assert ok.unwrap_or_else(lambda _: 0) == 100


class TestErr:
    @pytest.fixture
    def err(self) -> Err[str]:
        return Err("An error has occurred.")

    def test_and_(self, err: Err[str]) -> None:
        assert err.and_(Ok(100)) == err

    def test_and_then(self, err: Err[str]) -> None:
        assert err.and_then(lambda _: Ok(100)) == err

    def test_err(self, err: Err[str]) -> None:
        assert err.err() == Some("An error has occurred.")

    def test_inspect(self, err: Err[str]) -> None:
        func = mock.Mock()
        err.inspect(func)
        func.assert_not_called()

    def test_inspect_err(self, err: Err[str]) -> None:
        func = mock.Mock()
        err.inspect_err(func)
        func.assert_called_once_with("An error has occurred.")

    def test_map(self, err: Err[str]) -> None:
        assert err.map(lambda x: x * 2) == err

    def test_map_err(self, err: Err[str]) -> None:
        assert err.map_err(lambda x: x.upper()) == Err("AN ERROR HAS OCCURRED.")

    def test_map_or(self, err: Err[str]) -> None:
        assert err.map_or(lambda x: x * 2, 0) == 0

    def test_map_or_else(self, err: Err[str]) -> None:
        assert err.map_or_else(lambda x: x * 2, lambda _: 0) == 0

    def test_ok(self, err: Err[str]) -> None:
        assert err.ok() == Nothing

    def test_or_(self, err: Err[str]) -> None:
        assert err.or_(Ok(100)) == Ok(100)

    def test_or_else(self, err: Err[str]) -> None:
        assert err.or_else(lambda _: Ok(100)) == Ok(100)

    def test_unwrap(self, err: Err[str]) -> None:
        with pytest.raises(Panic):
            err.unwrap()

    def test_unwrap_err(self, err: Err[str]) -> None:
        assert err.unwrap_err() == "An error has occurred."

    def test_unwrap_or(self, err: Err[str]) -> None:
        assert err.unwrap_or(0) == 0

    def test_unwrap_or_else(self, err: Err[str]) -> None:
        assert err.unwrap_or_else(lambda _: 0) == 0
