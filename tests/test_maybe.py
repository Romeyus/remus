from typing import Any
from unittest import mock

import pytest

from remus import Err, Maybe, Nothing, Ok, Some
from remus._internal import Panic


# ==========================================
# ===            Some Tests                 ===
# ==========================================
class TestSome:
    @pytest.fixture
    def some(self) -> Maybe[int]:
        return Some(42)

    # ===============and_==============
    @pytest.mark.parametrize(
        ("maybe",),
        (
            pytest.param(Some("success")),
            pytest.param(Nothing),
        ),
    )
    def test_and_should_return_maybe(self, some: Maybe[int], maybe: Maybe[Any]) -> None:
        assert some.and_(maybe) is maybe

    # ===============and_then==============
    def test_and_then_should_return_factory_product(self, some: Maybe[int]) -> None:
        assert some.and_then(lambda v: Some(str(v))) == Some("42")

    def test_and_then_should_call_factory_with_inner_value(
        self, some: Maybe[int], factory: mock.Mock
    ) -> None:
        some.and_then(factory)
        factory.assert_called_once_with(42)

    # ===============expect==============
    def test_expect_should_return_inner_value(self, some: Maybe[int]) -> None:
        assert some.expect("testing expect") == 42

    # ===============filter==============
    def test_filter_should_return_self_if_predicate_is_true(
        self, some: Maybe[int]
    ) -> None:
        assert some.filter(lambda v: v > 40) is some

    def test_filter_should_return_nothing_if_predicate_is_false(
        self, some: Maybe[int]
    ) -> None:
        assert some.filter(lambda v: v > 50) is Nothing

    def test_filter_should_call_predicate_with_inner_value(
        self, some: Maybe[int], func: mock.Mock
    ) -> None:
        some.filter(func)
        func.assert_called_once_with(42)

    # ===============inspect==============
    def test_inspect_should_return_self(self, some: Maybe[int]) -> None:
        assert some.inspect(print) is some

    def test_inspect_should_call_func_with_inner_value(
        self, some: Maybe[int], func: mock.Mock
    ) -> None:
        some.inspect(func)
        func.assert_called_once_with(42)

    # ===============map==============
    def test_map_should_return_some_containing_factory_product(
        self, some: Maybe[int]
    ) -> None:
        assert some.map(str) == Some("42")

    def test_map_should_call_factory_with_inner_value(
        self, some: Maybe[int], factory: mock.Mock
    ) -> None:
        some.map(factory)
        factory.assert_called_once_with(42)

    # ===============map_or==============
    def test_map_or_should_return_factory_product(self, some: Maybe[int]) -> None:
        assert some.map_or(str, "hello") == "42"

    def test_map_or_should_call_factory_with_inner_value(
        self, some: Maybe[int], factory: mock.Mock
    ) -> None:
        some.map_or(factory, "hello")
        factory.assert_called_once_with(42)

    # ===============map_or_else==============
    def test_map_or_else_should_return_factory_product(self, some: Maybe[int]) -> None:
        assert some.map_or_else(str, lambda: "hello") == "42"

    def test_map_or_else_should_call_factory_with_inner_value(
        self, some: Maybe[int], factory: mock.Mock
    ) -> None:
        some.map_or_else(factory, lambda: "hello")
        factory.assert_called_once_with(42)

    def test_map_or_else_should_not_call_default_factory(
        self, some: Maybe[int], factory: mock.Mock
    ) -> None:
        some.map_or_else(str, factory)
        factory.assert_not_called()

    # ===============ok_or==============
    def test_ok_or_should_return_ok_containing_inner_value(
        self, some: Maybe[int]
    ) -> None:
        assert some.ok_or("failure") == Ok(42)

    # ===============ok_or_else==============
    def test_ok_or_else_should_return_ok_containing_inner_value(
        self, some: Maybe[int]
    ) -> None:
        assert some.ok_or_else(lambda: "failure") == Ok(42)

    def test_ok_or_else_should_not_call_factory(
        self, some: Maybe[int], factory: mock.Mock
    ) -> None:
        some.ok_or_else(factory)
        factory.assert_not_called()

    # ===============or_==============
    @pytest.mark.parametrize(
        ("maybe",),
        (
            pytest.param(Some(100)),
            pytest.param(Nothing),
        ),
    )
    def test_or_should_return_self(self, some: Maybe[int], maybe: Maybe[int]) -> None:
        assert some.or_(maybe) is some

    # ===============or_else==============
    def test_or_else_should_return_self(self, some: Maybe[int]) -> None:
        assert some.or_else(lambda: Some(100)) is some

    def test_or_else_should_not_call_factory(
        self, some: Maybe[int], factory: mock.Mock
    ) -> None:
        some.or_else(factory)
        factory.assert_not_called()

    # ===============unwrap==============
    def test_unwrap_should_return_inner_value(self, some: Maybe[int]) -> None:
        assert some.unwrap() == 42

    # ===============unwrap_or==============
    def test_unwrap_or_should_return_inner_value(self, some: Maybe[int]) -> None:
        assert some.unwrap_or(100) == 42

    # ===============unwrap_or_else==============
    def test_unwrap_or_else_should_return_inner_value(self, some: Maybe[int]) -> None:
        assert some.unwrap_or_else(lambda: 100) == 42

    def test_unwrap_or_else_should_not_call_default_factory(
        self, some: Maybe[int], factory: mock.Mock
    ) -> None:
        some.unwrap_or_else(factory)
        factory.assert_not_called()


# ==========================================
# ===            Nothing Tests                 ===
# ==========================================
class TestNothing:
    # ===============and_==============
    @pytest.mark.parametrize(
        ("maybe",),
        (
            pytest.param(Some("success")),
            pytest.param(Nothing),
        ),
    )
    def test_and_should_return_nothing(self, maybe: Maybe[Any]) -> None:
        assert Nothing.and_(maybe) is Nothing

    # ===============and_then==============
    def test_and_then_should_return_nothing(self) -> None:
        assert Nothing.and_then(lambda v: Some(str(v))) is Nothing

    def test_and_then_should_not_call_factory(self, factory: mock.Mock) -> None:
        Nothing.and_then(factory)
        factory.assert_not_called()

    # ===============expect==============
    def test_expect_should_panic_with_message(self) -> None:
        with pytest.raises(Panic, match="testing expect"):
            Nothing.expect("testing expect")

    # ===============filter==============
    def test_filter_should_return_nothing(self) -> None:
        assert Nothing.filter(lambda _: True) is Nothing

    def test_filter_should_not_call_predicate(self, func: mock.Mock) -> None:
        Nothing.filter(func)
        func.assert_not_called()

    # ===============inspect==============
    def test_inspect_should_return_nothing(self) -> None:
        assert Nothing.inspect(print) is Nothing

    def test_inspect_should_not_call_func(self, func: mock.Mock) -> None:
        Nothing.inspect(func)
        func.assert_not_called()

    # ===============map==============
    def test_map_should_return_nothing(self) -> None:
        assert Nothing.map(str) is Nothing

    def test_map_should_not_call_factory(self, factory: mock.Mock) -> None:
        Nothing.map(factory)
        factory.assert_not_called()

    # ===============map_or==============
    def test_map_or_should_return_default(self) -> None:
        assert Nothing.map_or(str, "hello") == "hello"

    def test_map_or_should_not_call_factory(self, factory: mock.Mock) -> None:
        Nothing.map_or(factory, "hello")
        factory.assert_not_called()

    # ===============map_or_else==============
    def test_map_or_else_should_return_default_factory_product(self) -> None:
        assert Nothing.map_or_else(str, lambda: "hello") == "hello"

    def test_map_or_else_should_call_default_factory(self, factory: mock.Mock) -> None:
        Nothing.map_or_else(str, factory)
        factory.assert_called_once()

    def test_map_or_else_should_not_call_factory(self, factory: mock.Mock) -> None:
        Nothing.map_or_else(factory, lambda: "hello")
        factory.assert_not_called()

    # ===============ok_or==============
    def test_ok_or_should_return_err_containing_err(self) -> None:
        assert Nothing.ok_or("failure") == Err("failure")

    # ===============ok_or_else==============
    def test_ok_or_else_should_return_err_containing_err(self) -> None:
        assert Nothing.ok_or_else(lambda: "failure") == Err("failure")

    def test_ok_or_else_should_call_factory(self, factory: mock.Mock) -> None:
        Nothing.ok_or_else(factory)
        factory.assert_called_once()

    # ===============or_==============
    @pytest.mark.parametrize(
        ("maybe",),
        (
            pytest.param(Some(100)),
            pytest.param(Nothing),
        ),
    )
    def test_or_should_return_maybe(self, maybe: Maybe[int]) -> None:
        assert Nothing.or_(maybe) is maybe

    # ===============or_else==============
    def test_or_else_should_return_factory_product(self) -> None:
        assert Nothing.or_else(lambda: Some(100)) == Some(100)

    def test_or_else_should_call_factory(self, factory: mock.Mock) -> None:
        Nothing.or_else(factory)
        factory.assert_called_once()

    # ===============unwrap==============
    def test_unwrap_should_panic(self) -> None:
        with pytest.raises(Panic):
            Nothing.unwrap()

    # ===============unwrap_or==============
    def test_unwrap_or_should_return_default(self) -> None:
        assert Nothing.unwrap_or(100) == 100

    # ===============unwrap_or_else==============
    def test_unwrap_or_else_should_return_default_factory_product(self) -> None:
        assert Nothing.unwrap_or_else(lambda: 100) == 100

    def test_unwrap_or_else_should_call_default_factory(
        self, factory: mock.Mock
    ) -> None:
        Nothing.unwrap_or_else(factory)
        factory.assert_called_once()
