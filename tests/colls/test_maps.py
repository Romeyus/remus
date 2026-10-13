from unittest import mock

import pytest

from remus import Err, Nothing, Ok, Some, colls, errs


# ==========================================
# ===            Map Tests                 ===
# ==========================================
class TestMap:
    @pytest.fixture
    def map(self) -> colls.Map[int, str]:
        return colls.Map(
            {
                200: "OK",
                201: "CREATED",
                302: "FOUND",
                303: "SEE OTHER",
                400: "BAD REQUEST",
                500: "INTERNAL SERVER ERROR",
            }
        )

    # ===============items==============
    def test_items_should_return_iterable_with_tuple_of_keys_and_values(
        self, map: colls.Map[int, str]
    ) -> None:
        assert list(map.items()) == [
            (200, "OK"),
            (201, "CREATED"),
            (302, "FOUND"),
            (303, "SEE OTHER"),
            (400, "BAD REQUEST"),
            (500, "INTERNAL SERVER ERROR"),
        ]

    # ===============keys==============
    def test_keys_should_return_iterable_with_keys(
        self, map: colls.Map[int, str]
    ) -> None:
        assert list(map.keys()) == [200, 201, 302, 303, 400, 500]

    # ===============get==============
    def test_get_should_return_some_containing_value_if_key_in_map(
        self, map: colls.Map[int, str]
    ) -> None:
        assert map.get(302) == Some("FOUND")

    def test_get_should_return_nothing_if_key_not_in_map(
        self, map: colls.Map[int, str]
    ) -> None:
        assert map.get(404) is Nothing

    # ===============get_or==============
    def test_get_or_should_return_value_if_key_in_map(
        self, map: colls.Map[int, str]
    ) -> None:
        assert map.get_or(302, "NOT FOUND") == "FOUND"

    def test_get_or_should_return_default_if_key_not_in_map(
        self, map: colls.Map[int, str]
    ) -> None:
        assert map.get_or(404, "NOT FOUND") == "NOT FOUND"

    # ===============get_or_else==============
    def test_get_or_else_should_return_value_if_key_in_map(
        self, map: colls.Map[int, str]
    ) -> None:
        assert map.get_or_else(302, lambda: "NOT FOUND") == "FOUND"

    def test_get_or_else_should_not_call_default_factory_if_key_in_map(
        self, map: colls.Map[int, str], factory: mock.Mock
    ) -> None:
        map.get_or_else(302, factory)
        factory.assert_not_called()

    def test_get_or_else_should_return_default_factory_product_if_key_not_in_map(
        self, map: colls.Map[int, str]
    ) -> None:
        assert map.get_or_else(404, lambda: "NOT FOUND") == "NOT FOUND"

    def test_get_or_else_should_call_default_factory_if_key_not_in_map(
        self, map: colls.Map[int, str], factory: mock.Mock
    ) -> None:
        map.get_or_else(404, factory)
        factory.assert_called_once()

    # ===============values==============
    def test_values_should_return_iterable_with_values(
        self, map: colls.Map[int, str]
    ) -> None:
        assert list(map.values()) == [
            "OK",
            "CREATED",
            "FOUND",
            "SEE OTHER",
            "BAD REQUEST",
            "INTERNAL SERVER ERROR",
        ]

    # ===============__contains__==============
    def test__contains__should_return_true_if_key_in_map(
        self, map: colls.Map[int, str]
    ) -> None:
        assert 200 in map

    # ===============__iter__==============
    def test__iter__should_return_iterator_of_keys(
        self, map: colls.Map[int, str]
    ) -> None:
        assert list(iter(map)) == [200, 201, 302, 303, 400, 500]

    # ===============__len__==============
    def test__len__should_return_length_of_map(self, map: colls.Map[int, str]) -> None:
        assert len(map) == 6


# ==========================================
# ===            MutMap Tests                 ===
# ==========================================
class TestMutMap:
    @pytest.fixture
    def map(self) -> colls.MutMap[int, str]:
        return colls.MutMap(
            {
                200: "OK",
                201: "CREATED",
                302: "FOUND",
                303: "SEE OTHER",
                400: "BAD REQUEST",
                500: "INTERNAL SERVER ERROR",
            }
        )

    # ===============clear==============
    def test_clear_should_remove_all_data(self, map: colls.MutMap[int, str]) -> None:
        map.clear()
        assert len(map) == 0

    # ===============pop==============
    def test_pop_should_return_ok_containing_value_if_key_in_map(
        self, map: colls.MutMap[int, str]
    ) -> None:
        assert map.pop(500) == Ok("INTERNAL SERVER ERROR")

    def test_pop_should_return_err_containing_key_err_with_key_if_key_not_in_map(
        self, map: colls.MutMap[int, str]
    ) -> None:
        assert map.pop(404) == Err(errs.KeyErr(404))

    def test_pop_should_remove_key_if_key_in_map(
        self, map: colls.MutMap[int, str]
    ) -> None:
        map.pop(500)
        assert 500 not in map

    # ===============pop_or==============
    def test_pop_or_should_return_value_if_key_in_map(
        self, map: colls.MutMap[int, str]
    ) -> None:
        assert map.pop_or(200, "TOO MANY REQUESTS") == "OK"

    def test_pop_or_should_return_default_if_key_not_in_map(
        self, map: colls.MutMap[int, str]
    ) -> None:
        assert map.pop_or(429, "TOO MANY REQUESTS") == "TOO MANY REQUESTS"

    # ===============pop_or_else==============
    def test_pop_or_else_should_return_value_if_key_in_map(
        self, map: colls.MutMap[int, str]
    ) -> None:
        assert map.pop_or_else(201, lambda: "UNAUTHORIZED") == "CREATED"

    def test_pop_or_else_should_return_default_factory_product_if_key_not_in_map(
        self, map: colls.MutMap[int, str]
    ) -> None:
        assert map.pop_or_else(401, lambda: "UNAUTHORIZED") == "UNAUTHORIZED"

    def test_pop_or_else_should_not_call_default_factory_if_key_in_map(
        self, map: colls.MutMap[int, str], factory: mock.Mock
    ) -> None:
        map.pop_or_else(201, factory)
        factory.assert_not_called()

    def test_pop_or_else_should_call_default_factory_if_key_not_in_map(
        self, map: colls.MutMap[int, str], factory: mock.Mock
    ) -> None:
        map.pop_or_else(401, factory)
        factory.assert_called_once()

    # ===============set==============
    def test_set_should_set_key_value_pair_in_map(
        self, map: colls.MutMap[int, str]
    ) -> None:
        map.set(403, "FORBIDDEN")
        assert map.get(403) == Some("FORBIDDEN")

    # ===============set_default==============
    def test_set_default_should_return_value_if_key_in_map(
        self, map: colls.MutMap[int, str]
    ) -> None:
        assert map.set_default(200, "PERMANENT REDIRECT") == "OK"

    def test_set_default_should_return_default_if_key_not_in_map(
        self, map: colls.MutMap[int, str]
    ) -> None:
        assert map.set_default(308, "PERMANENT REDIRECT") == "PERMANENT REDIRECT"
