from unittest import mock

import pytest

from remus import Err, Nothing, Ok, Result, Some
from remus._internal import Panic


class TestOk:
    @pytest.fixture
    def ok(self) -> Result[int, str]:
        return Ok(2)

    @pytest.mark.parametrize(
        ("result",),
        (
            pytest.param(Ok("different result type"), id="result-is-Ok"),
            pytest.param(Err("late error"), id="result-is-Err"),
        ),
    )
    def test_and_returns_result(
        self, ok: Result[int, str], result: Result[int, str]
    ) -> None:
        assert ok.and_(result) is result

    def test_and_then_applies_func(self, ok: Result[int, str]) -> None:
        assert ok.and_then(lambda v: Ok(v * 50)) == Ok(100)

    def test_and_then_calls_func_with_value(
        self, ok: Result[int, str], func: mock.Mock
    ) -> None:
        ok.and_then(func)
        func.assert_called_once_with(2)

    def test_err_returns_nothing(self, ok: Result[int, str]) -> None:
        assert ok.err() == Nothing

    def test_expect_returns_unwrapped_value(self, ok: Result[int, str]) -> None:
        assert ok.expect("testing expect") == 2

    def test_expect_err_panics_with_message(self, ok: Result[int, str]) -> None:
        with pytest.raises(Panic, match="testing expect_err"):
            ok.expect_err("testing expect_err")

    def test_inspect_calls_func_with_value(
        self, ok: Result[int, str], func: mock.Mock
    ) -> None:
        ok.inspect(func)
        func.assert_called_once_with(2)

    def test_inspect_err_does_not_call_func(
        self, ok: Result[int, str], func: mock.Mock
    ) -> None:
        ok.inspect_err(func)
        func.assert_not_called()

    def test_map_applies_func(self, ok: Result[int, str]) -> None:
        assert ok.map(lambda v: v**2) == Ok(4)

    def test_map_calls_func_with_value(
        self, ok: Result[int, str], func: mock.Mock
    ) -> None:
        ok.map(func)
        func.assert_called_once_with(2)

    def test_map_err_returns_self(self, ok: Result[int, str]) -> None:
        assert ok.map_err(lambda v: v.upper()) is ok

    def test_map_err_does_not_call_func(
        self, ok: Result[int, str], func: mock.Mock
    ) -> None:
        ok.map_err(func)
        func.assert_not_called()

    def test_map_or_applies_func(self, ok: Result[int, str]) -> None:
        assert ok.map_or(lambda v: v**2, 42) == 4

    def test_map_or_calls_func_with_value(
        self, ok: Result[int, str], func: mock.Mock
    ) -> None:
        ok.map_or(func, 42)
        func.assert_called_once_with(2)

    def test_map_or_else_applies_func(self, ok: Result[int, str]) -> None:
        assert ok.map_or_else(lambda v: v**2, lambda e: len(e)) == 4

    def test_map_or_else_calls_func_with_value(
        self, ok: Result[int, str], func: mock.Mock
    ) -> None:
        ok.map_or_else(func, lambda e: len(e))
        func.assert_called_once_with(2)

    def test_map_or_else_does_not_call_default_factory(
        self, ok: Result[int, str], func: mock.Mock
    ) -> None:
        ok.map_or_else(lambda v: v**2, func)
        func.assert_not_called()

    def test_ok_returns_some_with_value(self, ok: Result[int, str]) -> None:
        assert ok.ok() == Some(2)

    @pytest.mark.parametrize(
        ("result",),
        (
            pytest.param(Ok(100), id="result-is-Ok"),
            pytest.param(Err("late error"), id="result-is-Err"),
        ),
    )
    def test_or_returns_self(
        self, ok: Result[int, str], result: Result[int, str]
    ) -> None:
        assert ok.or_(result) is ok

    def test_or_else_returns_self(self, ok: Result[int, str]) -> None:
        assert ok.or_else(lambda v: Err(v.upper())) is ok

    def test_or_else_does_not_call_func(
        self, ok: Result[int, str], func: mock.Mock
    ) -> None:
        ok.or_else(func)
        func.assert_not_called()

    def test_unwrap_returns_unwrapped_value(self, ok: Result[int, str]) -> None:
        assert ok.unwrap() == 2

    def test_unwrap_err_panics(self, ok: Result[int, str]) -> None:
        with pytest.raises(Panic):
            ok.unwrap_err()

    def test_unwrap_or_returns_unwrapped_value(self, ok: Result[int, str]) -> None:
        assert ok.unwrap_or(42) == 2

    def test_unwrap_or_else_returns_unwrapped_value(self, ok: Result[int, str]) -> None:
        assert ok.unwrap_or_else(lambda _: 42) == 2

    def test_unwrap_or_else_does_not_call_func(
        self, ok: Result[int, str], func: mock.Mock
    ) -> None:
        ok.unwrap_or_else(func)
        func.assert_not_called()


class TestErr:
    @pytest.fixture
    def err(self) -> Result[int, str]:
        return Err("failure")

    @pytest.mark.parametrize(
        ("result",),
        (
            pytest.param(Ok("foo"), id="result-is-Ok"),
            pytest.param(Err("late error"), id="result-is-Err"),
        ),
    )
    def test_and_returns_self(
        self, err: Result[int, str], result: Result[str, str]
    ) -> None:
        assert err.and_(result) is err

    def test_and_then_returns_self(self, err: Result[int, str]) -> None:
        assert err.and_then(lambda v: Ok(v**2)) is err

    def test_and_then_does_not_call_func(
        self, err: Result[int, str], func: mock.Mock
    ) -> None:
        err.and_then(func)
        func.assert_not_called()

    def test_err_returns_some_with_value(self, err: Result[int, str]) -> None:
        assert err.err() == Some("failure")

    def test_expect_panics_with_message(self, err: Result[int, str]) -> None:
        with pytest.raises(Panic, match="testing expect"):
            err.expect("testing expect")

    def test_expect_err_returns_unwrapped_value(self, err: Result[int, str]) -> None:
        assert err.expect_err("testing expect_err") == "failure"

    def test_inspect_does_not_call_func(
        self, err: Result[int, str], func: mock.Mock
    ) -> None:
        err.inspect(func)
        func.assert_not_called()

    def test_inspect_err_calls_func_with_value(
        self, err: Result[int, str], func: mock.Mock
    ) -> None:
        err.inspect_err(func)
        func.assert_called_once_with("failure")

    def test_map_returns_self(self, err: Result[int, str]) -> None:
        assert err.map(lambda v: v**2) is err

    def test_map_does_not_call_func(
        self, err: Result[int, str], func: mock.Mock
    ) -> None:
        err.map(func)
        func.assert_not_called()

    def test_map_err_applies_func(self, err: Result[int, str]) -> None:
        assert err.map_err(lambda v: v.upper()) == Err("FAILURE")

    def test_map_calls_func_with_value(
        self, err: Result[int, str], func: mock.Mock
    ) -> None:
        err.map_err(func)
        func.assert_called_once_with("failure")

    def test_map_or_returns_default(self, err: Result[int, str]) -> None:
        assert err.map_or(lambda v: v**2, 42) == 42

    def test_map_or_else_applies_default_factory(self, err: Result[int, str]) -> None:
        assert err.map_or_else(lambda v: v**2, lambda e: len(e)) == 7

    def test_map_or_else_calls_default_factory_with_value(
        self, err: Result[int, str], func: mock.Mock
    ) -> None:
        err.map_or_else(lambda v: v**2, func)
        func.assert_called_once_with("failure")

    def test_map_or_else_does_not_call_func(
        self, err: Result[int, str], func: mock.Mock
    ) -> None:
        err.map_or_else(func, lambda e: len(e))
        func.assert_not_called()

    def test_ok_returns_nothing(self, err: Result[int, str]) -> None:
        assert err.ok() == Nothing

    @pytest.mark.parametrize(
        ("result",),
        (
            pytest.param(Ok(2), id="result-is-Ok"),
            pytest.param(Err("late error"), id="result-is-Err"),
        ),
    )
    def test_or_returns_result(
        self, err: Result[int, str], result: Result[int, str]
    ) -> None:
        assert err.or_(result) is result

    def test_or_else_returns_applies_func(self, err: Result[int, str]) -> None:
        assert err.or_else(lambda v: Ok(len(v))) == Ok(7)

    def test_or_else_calls_func_with_value(
        self, err: Result[int, str], func: mock.Mock
    ) -> None:
        err.or_else(func)
        func.assert_called_once_with("failure")

    def test_unwrap_panics(self, err: Result[int, str]) -> None:
        with pytest.raises(Panic):
            err.unwrap()

    def test_unwrap_err_returns_unwrapped_value(self, err: Result[int, str]) -> None:
        assert err.unwrap_err() == "failure"

    def test_unwrap_or_returns_default(self, err: Result[int, str]) -> None:
        assert err.unwrap_or(42) == 42

    def test_unwrap_or_else_applies_default_factory(
        self, err: Result[int, str]
    ) -> None:
        assert err.unwrap_or_else(lambda v: len(v)) == 7

    def test_unwrap_or_else_calls_default_factory_with_value(
        self, err: Result[int, str], func: mock.Mock
    ) -> None:
        err.unwrap_or_else(func)
        func.assert_called_once_with("failure")
