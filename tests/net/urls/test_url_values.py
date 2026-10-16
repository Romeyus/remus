import pytest

from remus import Nothing, Some, colls, strs
from remus.net import urls


# ==========================================
# ===            Headers Tests                 ===
# ==========================================
class TestHeaders:
    @pytest.fixture
    def headers(self) -> urls.Headers:
        return urls.Headers(
            colls.Map(
                {
                    strs.Lowercase("content-type"): colls.Array(["application/json"]),
                    strs.Lowercase("content-length"): colls.Array(["42"]),
                    strs.Lowercase("x-custom-header"): colls.Array(
                        ["value-1", "value-2"]
                    ),
                }
            )
        )

    # ===============get==============
    def test_get_should_return_first_value(self, headers: urls.Headers) -> None:
        assert headers.get("x-custom-header") == Some("value-1")

    def test_get_should_return_nothing_if_key_is_missing(
        self, headers: urls.Headers
    ) -> None:
        assert headers.get("missing-header") is Nothing

    # ===============get_all==============
    @pytest.mark.parametrize(
        ("key", "values"),
        (
            pytest.param("content-type", colls.Array(["application/json"])),
            pytest.param("content-length", colls.Array(["42"])),
            pytest.param("x-custom-header", colls.Array(["value-1", "value-2"])),
        ),
    )
    def test_get_all_should_return_all_values(
        self, headers: urls.Headers, key: str, values: colls.Array[str]
    ) -> None:
        assert headers.get_all(key) == values

    def test_get_all_should_normalise_key(self, headers: urls.Headers) -> None:
        assert headers.get_all("Content-Type") == headers.get_all("content-type")

    def test_get_all_should_return_empty_array_if_key_is_missing(
        self, headers: urls.Headers
    ) -> None:
        assert headers.get_all("missing-header") == colls.Array()

    # ===============items==============
    def test_items_should_return_iter_with_keys_and_values(
        self, headers: urls.Headers
    ) -> None:
        assert list(headers.items()) == [
            ("content-type", "application/json"),
            ("content-length", "42"),
            ("x-custom-header", "value-1"),
            ("x-custom-header", "value-2"),
        ]

    # ===============__contains__==============
    @pytest.mark.parametrize(
        ("key", "expected"),
        (
            pytest.param("content-type", True),
            pytest.param("missing-header", False),
        ),
    )
    def test__contains__should_return_bool(
        self, headers: urls.Headers, key: str, expected: bool
    ) -> None:
        assert (key in headers) is expected

    def test__contains__should_normalise_key(self, headers: urls.Headers) -> None:
        assert "Content-Type" in headers
