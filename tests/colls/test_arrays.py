from unittest import mock

import pytest

from remus import Err, Nothing, Ok, Some, colls, errs


# ==========================================
# ===            Array Tests                 ===
# ==========================================
class TestArray:
    @pytest.fixture
    def array(self) -> colls.Array[str]:
        return colls.Array(
            (
                "apple",
                "banana",
                "orange",
                "banana",
            )
        )

    # ===============count==============
    @pytest.mark.parametrize(
        ("value", "count"),
        (
            pytest.param("apple", 1),
            pytest.param("banana", 2),
            pytest.param("orange", 1),
        ),
    )
    def test_count_should_return_number_of_times_value_in_array(
        self, array: colls.Array[str], value: str, count: int
    ) -> None:
        assert array.count(value) == count

    # ===============first==============
    def test_first_should_return_some_containing_first_value_in_array(
        self, array: colls.Array[str]
    ) -> None:
        assert array.first() == Some("apple")

    def test_first_should_return_nothing_if_array_is_empty(self) -> None:
        assert colls.Array().first() is Nothing

    # ===============get==============
    @pytest.mark.parametrize(
        ("index", "value"),
        (
            pytest.param(0, "apple"),
            pytest.param(1, "banana"),
            pytest.param(2, "orange"),
            pytest.param(3, "banana"),
        ),
    )
    def test_get_should_return_some_containing_value_if_index_in_range(
        self, array: colls.Array[str], index: int, value: str
    ) -> None:
        assert array.get(index) == Some(value)

    def test_get_should_return_nothing_if_index_out_of_range(
        self, array: colls.Array[str]
    ) -> None:
        assert array.get(42) is Nothing

    # ===============get_or==============
    def test_get_or_should_return_value_if_index_in_range(
        self, array: colls.Array[str]
    ) -> None:
        assert array.get_or(0, "mango") == "apple"

    def test_get_or_should_return_default_if_index_out_of_range(
        self, array: colls.Array[str]
    ) -> None:
        assert array.get_or(42, "mango") == "mango"

    # ===============get_or_else==============
    def test_get_or_else_should_return_value_if_index_in_range(
        self, array: colls.Array[str]
    ) -> None:
        assert array.get_or_else(1, lambda: "mango") == "banana"

    def test_get_or_else_should_return_default_factory_product_if_index_out_of_range(
        self, array: colls.Array[str]
    ) -> None:
        assert array.get_or_else(42, lambda: "mango") == "mango"

    def test_get_or_else_should_call_default_factory_if_index_out_of_range(
        self, array: colls.Array[str], factory: mock.Mock
    ) -> None:
        array.get_or_else(42, factory)
        factory.assert_called_once()

    def test_get_or_else_should_not_call_default_factory_if_index_in_range(
        self, array: colls.Array[str], factory: mock.Mock
    ) -> None:
        array.get_or_else(0, factory)
        factory.assert_not_called()

    # ===============index==============
    @pytest.mark.parametrize(
        ("value", "index"),
        (
            pytest.param("apple", 0),
            pytest.param("banana", 1),
            pytest.param("orange", 2),
        ),
    )
    def test_index_should_return_some_containing_first_index_if_value_in_array(
        self, array: colls.Array[str], value: str, index: int
    ) -> None:
        assert array.index(value) == Some(index)

    def test_index_should_return_nothing_if_value_not_in_array(
        self, array: colls.Array[str]
    ) -> None:
        assert array.index("mango") is Nothing

    # ===============last==============
    def test_last_should_return_some_containing_last_value_in_array(
        self, array: colls.Array[str]
    ) -> None:
        assert array.last() == Some("banana")

    def test_last_should_return_nothing_if_array_is_empty(self) -> None:
        assert colls.Array().last() is Nothing

    # ===============__contains__==============
    def test__contains__should_return_true_if_value_in_array(
        self, array: colls.Array[str]
    ) -> None:
        assert "apple" in array

    def test__contains__should_return_false_if_value_not_in_array(
        self, array: colls.Array[str]
    ) -> None:
        assert "mango" not in array

    # ===============__iter__==============
    def test__iter__should_return_iterator_of_values(
        self, array: colls.Array[str]
    ) -> None:
        assert list(iter(array)) == ["apple", "banana", "orange", "banana"]

    # ===============__len__==============
    def test__len__should_return_length_of_array(self, array: colls.Array[str]) -> None:
        assert len(array) == 4


# ==========================================
# ===            MutArray Tests                 ===
# ==========================================
class TestMutArray:
    @pytest.fixture
    def array(self) -> colls.MutArray[str]:
        return colls.MutArray(
            [
                "apple",
                "banana",
                "orange",
                "banana",
            ]
        )

    # ===============append==============
    def test_append_should_add_value_to_end_of_array(
        self, array: colls.MutArray[str]
    ) -> None:
        array.append("mango")
        assert array.last() == Some("mango")

    # ===============clear==============
    def test_clear_should_remove_all_values_from_array(
        self, array: colls.MutArray[str]
    ) -> None:
        array.clear()
        assert len(array) == 0

    # ===============insert==============
    def test_insert_should_add_value_at_index(self, array: colls.MutArray[str]) -> None:
        array.insert(2, "mango")
        assert array.get(2) == Some("mango")

    # ===============pop==============
    @pytest.mark.parametrize(
        ("index", "value"),
        (
            pytest.param(0, "apple"),
            pytest.param(1, "banana"),
            pytest.param(2, "orange"),
            pytest.param(3, "banana"),
        ),
    )
    def test_pop_should_return_ok_containing_value_if_index_in_range(
        self, array: colls.MutArray[str], index: int, value: str
    ) -> None:
        assert array.pop(index) == Ok(value)

    def test_pop_should_return_err_containing_index_err_if_index_out_of_range(
        self, array: colls.MutArray[str]
    ) -> None:
        assert array.pop(42) == Err(errs.IndexErr(42))

    def test_pop_should_remove_value_if_index_in_range(
        self, array: colls.MutArray[str]
    ) -> None:
        array.pop(0)
        assert "apple" not in array

    # ===============pop_or==============
    def test_pop_or_should_return_value_if_index_in_range(
        self, array: colls.MutArray[str]
    ) -> None:
        assert array.pop_or(1, "mango") == "banana"

    def test_pop_or_should_return_default_if_index_out_of_range(
        self, array: colls.MutArray[str]
    ) -> None:
        assert array.pop_or(42, "mango") == "mango"

    # ===============pop_or_else==============
    def test_pop_or_else_should_return_value_if_index_in_range(
        self, array: colls.MutArray[str]
    ) -> None:
        assert array.pop_or_else(2, lambda: "pear") == "orange"

    def test_pop_or_else_should_return_default_factory_product_if_index_out_of_range(
        self, array: colls.MutArray[str]
    ) -> None:
        assert array.pop_or_else(42, lambda: "pear") == "pear"

    def test_pop_or_else_should_call_default_factory_if_index_out_of_range(
        self, array: colls.MutArray[str], factory: mock.Mock
    ) -> None:
        array.pop_or_else(42, factory)
        factory.assert_called_once()

    def test_pop_or_else_should_not_call_default_factory_if_index_in_range(
        self, array: colls.MutArray[str], factory: mock.Mock
    ) -> None:
        array.pop_or_else(0, factory)
        factory.assert_not_called()

    # ===============prepend==============
    def test_prepend_should_add_value_to_start_of_array(
        self, array: colls.MutArray[str]
    ) -> None:
        array.prepend("mango")
        assert array.first() == Some("mango")

    # ===============remove==============
    def test_remove_should_return_ok_containing_none_if_value_in_array(
        self, array: colls.MutArray[str]
    ) -> None:
        assert array.remove("banana") == Ok(None)

    def test_remove_should_return_err_containing_index_err_if_value_not_in_array(
        self, array: colls.MutArray[str]
    ) -> None:
        result = array.remove("mango")
        assert isinstance(result, Err) and result.value.value == "mango"

    # ===============set==============
    def test_set_should_return_some_containing_none_if_index_in_range(
        self, array: colls.MutArray[str]
    ) -> None:
        assert array.set(1, "peach") == Ok(None)

    def test_set_should_return_err_containing_index_err_if_index_out_of_range(
        self, array: colls.MutArray[str]
    ) -> None:
        assert array.set(42, "peach") == Err(errs.IndexErr(42))
