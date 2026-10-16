import pytest

from remus._internal import Panic
from remus.net import urls


class TestPath:
    @pytest.mark.parametrize(
        ("input", "expected"),
        (
            pytest.param("", "/"),
            pytest.param("/", "/"),
            pytest.param("hello", "/hello"),
            pytest.param("/hello", "/hello"),
        ),
    )
    def test_path_should_add_leading_slash_if_does_not_have_one(
        self, input: str, expected: str
    ) -> None:
        assert urls.Path(input) == urls.Path(expected)

    @pytest.mark.parametrize(
        ("input", "expected"),
        (
            pytest.param("//", "/"),
            pytest.param("//hello", "/hello"),
            pytest.param("//hello//world", "/hello/world"),
        ),
    )
    def test_path_should_remove_duplicate_slashes(
        self, input: str, expected: str
    ) -> None:
        assert urls.Path(input) == urls.Path(expected)

    @pytest.mark.parametrize(
        ("input", "expected"),
        (
            pytest.param("///", "/"),
            pytest.param("hello/", "/hello"),
            pytest.param("hello//", "/hello"),
            pytest.param("hello/world/", "/hello/world"),
        ),
    )
    def test_path_should_remove_all_trailing_slashes(
        self, input: str, expected: str
    ) -> None:
        assert urls.Path(input) == urls.Path(expected)

    @pytest.mark.parametrize(
        ("input",),
        (
            pytest.param(".."),
            pytest.param("../"),
            pytest.param("../src"),
            pytest.param("src/../secret"),
        ),
    )
    def test_path_should_panic_on_parent_directory_segments(self, input: str) -> None:
        with pytest.raises(Panic):
            urls.Path(input)

    @pytest.mark.parametrize(
        ("input", "expected"),
        (
            pytest.param(".", "/."),
            pytest.param("hello.txt", "/hello.txt"),
            pytest.param("hello.css", "/hello.css"),
            pytest.param("hello/world.js", "/hello/world.js"),
        ),
    )
    def test_path_should_allow_single_dot_segments(
        self, input: str, expected: str
    ) -> None:
        assert urls.Path(input) == urls.Path(expected)
