from unittest import mock

import pytest

from remus import Err, Maybe, Nothing, Ok, Some
from remus._internal import Panic


class TestSome:
    @pytest.fixture
    def some(self) -> Maybe[int]:
        return Some(2)

    @pytest.mark.parametrize(
        ("maybe",),
        (
            pytest.param(Some("foo"), id="maybe-is-Some"),
            pytest.param(Nothing, id="maybe-is-Nothing"),
        ),
    )
    def test_and_returns_maybe(self, some: Maybe[int], maybe: Maybe[str]) -> None:
        assert some.and_(maybe) is maybe

    def test_and_then_applies_func(self, some: Maybe[int]) -> None:
        assert some.and_then(lambda v: Some(v * 50)) == Some(100)

    def test_and_then_calls_func_with_value(
        self, some: Maybe[int], func: mock.Mock
    ) -> None:
        some.and_then(func)
        func.assert_called_once_with(2)

    def test_expect_returns_unwrapped_value(self, some: Maybe[int]) -> None:
        assert some.expect("testing expect") == 2

    def test_filter_returns_self_when_predicate_is_true(self, some: Maybe[int]) -> None:
        assert some.filter(lambda v: v % 2 == 0) is some

    def test_filter_returns_nothing_when_predicate_is_false(self) -> None:
        assert Some(3).filter(lambda v: v % 2 == 0) is Nothing

    def test_filter_calls_predicate_with_value(
        self, some: Maybe[int], func: mock.Mock
    ) -> None:
        some.filter(func)
        func.assert_called_once_with(2)

    def test_inspect_calls_func_with_value(
        self, some: Maybe[int], func: mock.Mock
    ) -> None:
        some.inspect(func)
        func.assert_called_once_with(2)

    def test_map_applies_func(self, some: Maybe[int]) -> None:
        assert some.map(lambda v: v**2) == Some(4)

    def test_map_calls_func_with_value(self, some: Maybe[int], func: mock.Mock) -> None:
        some.map(func)
        func.assert_called_once_with(2)

    def test_map_or_applies_func(self, some: Maybe[int]) -> None:
        assert some.map_or(lambda v: v**2, 42) == 4

    def test_map_or_calls_func_with_value(
        self, some: Maybe[int], func: mock.Mock
    ) -> None:
        some.map_or(func, 42)
        func.assert_called_once_with(2)

    def test_map_or_else_applies_func(self, some: Maybe[int]) -> None:
        assert some.map_or_else(lambda v: v**2, lambda: 42) == 4

    def test_map_or_else_calls_func_with_value(
        self, some: Maybe[int], func: mock.Mock
    ) -> None:
        some.map_or_else(func, lambda: 42)
        func.assert_called_once_with(2)

    def test_map_or_else_does_not_call_default_factory(
        self, some: Maybe[int], func: mock.Mock
    ) -> None:
        some.map_or_else(lambda v: v**2, func)
        func.assert_not_called()

    def test_ok_or_returns_ok_with_value(self, some: Maybe[int]) -> None:
        assert some.ok_or("failure") == Ok(2)

    def test_ok_or_else_returns_ok_with_value(self, some: Maybe[int]) -> None:
        assert some.ok_or_else(lambda: "failure") == Ok(2)

    def test_ok_or_else_does_not_call_func(
        self, some: Maybe[int], func: mock.Mock
    ) -> None:
        some.ok_or_else(func)
        func.assert_not_called()

    @pytest.mark.parametrize(
        ("maybe",),
        (
            pytest.param(Some(42), id="maybe-is-Some"),
            pytest.param(Nothing, id="maybe-is-Nothing"),
        ),
    )
    def test_or_returns_self(self, some: Maybe[int], maybe: Maybe[int]) -> None:
        assert some.or_(maybe) is some

    def test_or_else_returns_self(self, some: Maybe[int]) -> None:
        assert some.or_else(lambda: Some(42)) is some

    def test_or_else_does_not_call_func(
        self, some: Maybe[int], func: mock.Mock
    ) -> None:
        some.or_else(func)
        func.assert_not_called()

    def test_unwrap_returns_unwrapped_value(self, some: Maybe[int]) -> None:
        assert some.unwrap() == 2

    def test_unwrap_or_returns_unwrapped_value(self, some: Maybe[int]) -> None:
        assert some.unwrap_or(42) == 2

    def test_unwrap_or_else_returns_unwrapped_value(self, some: Maybe[int]) -> None:
        assert some.unwrap_or_else(lambda: 42) == 2

    def test_unwrap_or_else_does_not_call_func(
        self, some: Maybe[int], func: mock.Mock
    ) -> None:
        some.unwrap_or_else(func)
        func.assert_not_called()


class TestNothing:
    @pytest.mark.parametrize(
        ("maybe",),
        (
            pytest.param(Some("foo"), id="maybe-is-Some"),
            pytest.param(Nothing, id="maybe-is-Nothing"),
        ),
    )
    def test_and_returns_nothing(self, maybe: Maybe[int]) -> None:
        assert Nothing.and_(maybe) is Nothing

    def test_and_then_returns_nothing(self) -> None:
        assert Nothing.and_then(lambda v: Some(v * 50)) is Nothing

    def test_and_then_does_not_call_func(self, func: mock.Mock) -> None:
        Nothing.and_then(func)
        func.assert_not_called()

    def test_expect_panics_with_message(self) -> None:
        with pytest.raises(Panic, match="testing expect"):
            Nothing.expect("testing expect")

    def test_filter_returns_nothing(self) -> None:
        assert Nothing.filter(lambda v: v % 2 == 0) is Nothing

    def test_filter_does_not_call_predicate(self, func: mock.Mock) -> None:
        Nothing.filter(func)
        func.assert_not_called()

    def test_inspect_does_not_call_func(self, func: mock.Mock) -> None:
        Nothing.inspect(func)
        func.assert_not_called()

    def test_map_returns_nothing(self) -> None:
        assert Nothing.map(lambda v: v**2) is Nothing

    def test_map_does_not_call_func(self, func: mock.Mock) -> None:
        Nothing.map(func)
        func.assert_not_called()

    def test_map_or_returns_default(self) -> None:
        assert Nothing.map_or(lambda v: v**2, 42) == 42

    def test_map_or_does_not_call_func(self, func: mock.Mock) -> None:
        Nothing.map_or(func, 42)
        func.assert_not_called()

    def test_map_or_else_applies_default_factory(self) -> None:
        assert Nothing.map_or_else(lambda v: v**2, lambda: 42) == 42

    def test_map_or_else_calls_default_factory(self, func: mock.Mock) -> None:
        Nothing.map_or_else(lambda v: v**2, func)
        func.assert_called_once()

    def test_map_or_else_does_not_call_func(self, func: mock.Mock) -> None:
        Nothing.map_or_else(func, lambda: 42)
        func.assert_not_called()

    def test_ok_or_returns_err(self) -> None:
        assert Nothing.ok_or("failure") == Err("failure")

    def test_ok_or_else_applies_func(self) -> None:
        assert Nothing.ok_or_else(lambda: "failure") == Err("failure")

    def test_ok_or_else_calls_func(self, func: mock.Mock) -> None:
        Nothing.ok_or_else(func)
        func.assert_called_once()

    @pytest.mark.parametrize(
        ("maybe",),
        (
            pytest.param(Some(42), id="maybe-is-Some"),
            pytest.param(Nothing, id="maybe-is-Nothing"),
        ),
    )
    def test_or_returns_maybe(self, maybe: Maybe[int]) -> None:
        assert Nothing.or_(maybe) is maybe

    def test_or_else_applies_func(self) -> None:
        assert Nothing.or_else(lambda: Some(42)) == Some(42)

    def test_or_else_calls_func(self, func: mock.Mock) -> None:
        Nothing.or_else(func)
        func.assert_called_once()

    def test_unwrap_panics(self) -> None:
        with pytest.raises(Panic):
            Nothing.unwrap()

    def test_unwrap_or_returns_default(self) -> None:
        assert Nothing.unwrap_or(42) == 42

    def test_unwrap_or_else_applies_func(self) -> None:
        assert Nothing.unwrap_or_else(lambda: 42) == 42

    def test_unwrap_or_else_calls_func(self, func: mock.Mock) -> None:
        Nothing.unwrap_or_else(func)
        func.assert_called_once()
