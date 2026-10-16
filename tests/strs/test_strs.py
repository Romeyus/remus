import pytest

from remus import strs


class TestLowercase:
    @pytest.mark.parametrize(
        ("input", "expected"),
        (
            pytest.param("hello", "hello"),
            pytest.param("HELLO", "hello"),
            pytest.param("Hello", "hello"),
            pytest.param("Hello world", "hello world"),
        ),
    )
    def test_lowercase_converts_all_strs_to_lowercase(
        self, input: str, expected: str
    ) -> None:
        assert strs.Lowercase(input) == strs.Lowercase(expected)
