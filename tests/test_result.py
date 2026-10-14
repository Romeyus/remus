from typing import Any
from unittest import mock

import pytest

from remus import Err, Nothing, Ok, Result, Some
from remus._internal import Panic


# ==========================================
# ===            Ok Tests                 ===
# ==========================================
class TestOk:
    @pytest.fixture
    def ok(self) -> Result[int, str]:
        return Ok(42)

    # ===============and_==============
    @pytest.mark.parametrize(
        ("result",),
        (
            pytest.param(Ok("success")),
            pytest.param(Err("failure")),
        ),
    )
    def test_and_should_return_result(
        self, ok: Result[int, str], result: Result[Any, str]
    ) -> None:
        assert ok.and_(result) is result

    # ===============and_then==============
    def test_and_then_should_return_factory_product(self, ok: Result[int, str]) -> None:
        assert ok.and_then(lambda v: Ok(str(v * 2))) == Ok("84")

    def test_and_then_should_call_factory_with_inner_value(
        self, ok: Result[int, str], factory: mock.Mock
    ) -> None:
        ok.and_then(factory)
        factory.assert_called_once_with(42)

    # ===============err==============
    def test_err_should_return_nothing(self, ok: Result[int, str]) -> None:
        assert ok.err() is Nothing

    # ===============expect==============
    def test_expect_should_return_inner_value(self, ok: Result[int, str]) -> None:
        assert ok.expect("testing expect") == 42

    # ===============expect_err==============
    def test_expect_err_should_panic_with_message(self, ok: Result[int, str]) -> None:
        with pytest.raises(Panic, match="testing expect_err"):
            ok.expect_err("testing expect_err")

    # ===============inspect==============
    def test_inspect_should_return_self(self, ok: Result[int, str]) -> None:
        assert ok.inspect(print) is ok

    def test_inspect_should_call_func_with_inner_value(
        self, ok: Result[int, str], func: mock.Mock
    ) -> None:
        ok.inspect(func)
        func.assert_called_once_with(42)

    # ===============inspect_err==============
    def test_inspect_err_should_return_self(self, ok: Result[int, str]) -> None:
        assert ok.inspect_err(print) is ok

    def test_inspect_err_should_not_call_func(
        self, ok: Result[int, str], func: mock.Mock
    ) -> None:
        ok.inspect_err(func)
        func.assert_not_called()

    # ===============map==============
    def test_map_should_return_ok_containing_factory_product(
        self, ok: Result[int, str]
    ) -> None:
        assert ok.map(lambda v: v % 2 == 0) == Ok(True)

    def test_map_should_call_factory_with_inner_value(
        self, ok: Result[int, str], factory: mock.Mock
    ) -> None:
        ok.map(factory)
        factory.assert_called_once_with(42)

    # ===============map_err==============
    def test_map_err_should_return_self(self, ok: Result[int, str]) -> None:
        assert ok.map_err(str.upper) is ok

    def test_map_err_should_not_call_factory(
        self, ok: Result[int, str], factory: mock.Mock
    ) -> None:
        ok.map_err(factory)
        factory.assert_not_called()

    # ===============map_or==============
    def test_map_or_should_return_factory_product(self, ok: Result[int, str]) -> None:
        assert ok.map_or(lambda v: v % 2 == 0, False) is True

    def test_map_or_should_call_factory_with_inner_value(
        self, ok: Result[int, str], factory: mock.Mock
    ) -> None:
        ok.map_or(factory, False)
        factory.assert_called_once_with(42)

    # ===============map_or_else==============
    def test_map_or_else_should_return_factory_product(
        self, ok: Result[int, str]
    ) -> None:
        assert ok.map_or_else(lambda v: v % 2 == 0, bool) is True

    def test_map_or_else_should_call_factory_with_inner_value(
        self, ok: Result[int, str], factory: mock.Mock
    ) -> None:
        ok.map_or_else(factory, bool)
        factory.assert_called_once_with(42)

    def test_map_or_else_should_not_call_default_factory(
        self, ok: Result[int, str], factory: mock.Mock
    ) -> None:
        ok.map_or_else(lambda v: v % 2 == 0, factory)
        factory.assert_not_called()

    # ===============ok==============
    def test_ok_should_return_some_containing_inner_value(
        self, ok: Result[int, str]
    ) -> None:
        assert ok.ok() == Some(42)

    # ===============or_==============
    @pytest.mark.parametrize(
        ("result",),
        (
            pytest.param(Ok("success")),
            pytest.param(Err("failure")),
        ),
    )
    def test_or_should_return_self(
        self, ok: Result[int, str], result: Result[Any, str]
    ) -> None:
        assert ok.or_(result) is ok

    # ===============or_else==============
    def test_or_else_should_return_self(self, ok: Result[int, str]) -> None:
        assert ok.or_else(lambda v: Err(v.upper())) is ok

    def test_or_else_should_not_call_factory(
        self, ok: Result[int, str], factory: mock.Mock
    ) -> None:
        ok.or_else(factory)
        factory.assert_not_called()

    # ===============unwrap==============
    def test_unwrap_should_return_inner_value(self, ok: Result[int, str]) -> None:
        assert ok.unwrap() == 42

    # ===============unwrap_err==============
    def test_unwrap_err_should_panic(self, ok: Result[int, str]) -> None:
        with pytest.raises(Panic):
            ok.unwrap_err()

    # ===============unwrap_or==============
    def test_unwrap_or_should_return_inner_value(self, ok: Result[int, str]) -> None:
        assert ok.unwrap_or(100) == 42

    # ===============unwrap_or_else==============
    def test_unwrap_or_else_should_return_inner_value(
        self, ok: Result[int, str]
    ) -> None:
        assert ok.unwrap_or_else(int) == 42

    def test_unwrap_or_else_should_not_call_default_factory(
        self, ok: Result[int, str], factory: mock.Mock
    ) -> None:
        ok.unwrap_or_else(factory)
        factory.assert_not_called()


# ==========================================
# ===            Err Tests                 ===
# ==========================================
class TestErr:
    @pytest.fixture
    def err(self) -> Result[int, str]:
        return Err("failure")

    # ===============and_==============
    @pytest.mark.parametrize(
        ("result",),
        (
            pytest.param(Ok("success")),
            pytest.param(Err(500)),
        ),
    )
    def test_and_should_return_self(
        self, err: Result[int, str], result: Result[Any, str]
    ) -> None:
        assert err.and_(result) is err

    # ===============and_then==============
    def test_and_then_should_return_self(self, err: Result[int, str]) -> None:
        assert err.and_then(lambda v: Ok(str(v * 2))) is err

    def test_and_then_should_not_call_factory(
        self, err: Result[int, str], factory: mock.Mock
    ) -> None:
        err.and_then(factory)
        factory.assert_not_called()

    # ===============err==============
    def test_err_should_return_some_containing_inner_value(
        self, err: Result[int, str]
    ) -> None:
        assert err.err() == Some("failure")

    # ===============expect==============
    def test_expect_should_panic_with_message(self, err: Result[int, str]) -> None:
        with pytest.raises(Panic, match="testing expect"):
            err.expect("testing expect")

    # ===============expect_err==============
    def test_expect_err_should_return_inner_value(self, err: Result[int, str]) -> None:
        assert err.expect_err("testing expect_err") == "failure"

    # ===============inspect==============
    def test_inspect_should_return_self(self, err: Result[int, str]) -> None:
        assert err.inspect(print) is err

    def test_inspect_should_not_call_func(
        self, err: Result[int, str], func: mock.Mock
    ) -> None:
        err.inspect(func)
        func.assert_not_called()

    # ===============inspect_err==============
    def test_inspect_err_should_return_self(self, err: Result[int, str]) -> None:
        assert err.inspect_err(print) is err

    def test_inspect_err_should_call_func_with_inner_value(
        self, err: Result[int, str], func: mock.Mock
    ) -> None:
        err.inspect_err(func)
        func.assert_called_once_with("failure")

    # ===============map==============
    def test_map_should_return_self(self, err: Result[int, str]) -> None:
        assert err.map(lambda v: v % 2 == 0) is err

    def test_map_should_not_call_factory(
        self, err: Result[int, str], factory: mock.Mock
    ) -> None:
        err.map(factory)
        factory.assert_not_called()

    # ===============map_err==============
    def test_map_err_should_return_err_containing_factory_product(
        self, err: Result[int, str]
    ) -> None:
        assert err.map_err(str.upper) == Err("FAILURE")

    def test_map_err_should_call_factory_with_inner_value(
        self, err: Result[int, str], factory: mock.Mock
    ) -> None:
        err.map_err(factory)
        factory.assert_called_once_with("failure")

    # ===============map_or==============
    def test_map_or_should_return_default(self, err: Result[int, str]) -> None:
        assert err.map_or(lambda v: v % 2 == 0, False) is False

    def test_map_or_should_not_call_factory(
        self, err: Result[int, str], factory: mock.Mock
    ) -> None:
        err.map_or(factory, False)
        factory.assert_not_called()

    # ===============map_or_else==============
    def test_map_or_else_should_return_default_factory_product(
        self, err: Result[int, str]
    ) -> None:
        assert err.map_or_else(lambda v: v % 2 == 0, len) == 7

    def test_map_or_else_should_call_default_factory_with_inner_value(
        self, err: Result[int, str], factory: mock.Mock
    ) -> None:
        err.map_or_else(bool, factory)
        factory.assert_called_once_with("failure")

    def test_map_or_else_should_not_call_factory(
        self, err: Result[int, str], factory: mock.Mock
    ) -> None:
        err.map_or_else(factory, len)
        factory.assert_not_called()

    # ===============ok==============
    def test_ok_should_return_nothing(self, err: Result[int, str]) -> None:
        assert err.ok() is Nothing

    # ===============or_==============
    @pytest.mark.parametrize(
        ("result",),
        (
            pytest.param(Ok("success")),
            pytest.param(Err(500)),
        ),
    )
    def test_or_should_return_result(
        self, err: Result[int, str], result: Result[Any, str]
    ) -> None:
        assert err.or_(result) is result

    # ===============or_else==============
    def test_or_else_should_return_factory_product(self, err: Result[int, str]) -> None:
        assert err.or_else(lambda v: Ok(len(v))) == Ok(7)

    def test_or_else_should_call_factory_with_inner_value(
        self, err: Result[int, str], factory: mock.Mock
    ) -> None:
        err.or_else(factory)
        factory.assert_called_once_with("failure")

    # ===============unwrap==============
    def test_unwrap_should_panic(self, err: Result[int, str]) -> None:
        with pytest.raises(Panic):
            err.unwrap()

    # ===============unwrap_err==============
    def test_unwrap_err_should_return_inner_value(self, err: Result[int, str]) -> None:
        assert err.unwrap_err() == "failure"

    # ===============unwrap_or==============
    def test_unwrap_or_should_return_default(self, err: Result[int, str]) -> None:
        assert err.unwrap_or(100) == 100

    # ===============unwrap_or_else==============
    def test_unwrap_or_else_should_return_default_factory_product(
        self, err: Result[int, str]
    ) -> None:
        assert err.unwrap_or_else(len) == 7

    def test_unwrap_or_else_should_call_default_factory_with_inner_value(
        self, err: Result[int, str], factory: mock.Mock
    ) -> None:
        err.unwrap_or_else(factory)
        factory.assert_called_once_with("failure")
