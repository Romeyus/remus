from http import HTTPMethod

import pytest

from remus import Err, Ok, colls
from remus.net import urls


# ==========================================
# ===            Path Tests                 ===
# ==========================================
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


# ==========================================
# ===            Router Tests                 ===
# ==========================================
class TestRouter:
    @pytest.fixture
    def router(self) -> urls.Router[str]:
        return urls.Router()

    # ===============map==============
    @pytest.mark.parametrize(
        ("path", "method"),
        (
            pytest.param("/", HTTPMethod.GET),
            pytest.param("/hello", HTTPMethod.POST),
            pytest.param("/hello/world", HTTPMethod.PUT),
        ),
    )
    def test_map_should_add_static_path(
        self, router: urls.Router[str], path: str, method: HTTPMethod
    ) -> None:
        router.map(urls.Path(path), method, "Hello world!")
        assert router.match(urls.Path(path), method) == Ok(
            urls.RouteMatch("Hello world!", colls.Map())
        )

    @pytest.mark.parametrize(
        ("registered_path", "request_path", "params"),
        (
            pytest.param(
                "/users/:user_id", "/users/123", colls.Map({"user_id": "123"})
            ),
            pytest.param(
                "/hello/:message",
                "/hello/greetings",
                colls.Map({"message": "greetings"}),
            ),
            pytest.param(
                "/hello/world/:greeting",
                "/hello/world/wassup",
                colls.Map({"greeting": "wassup"}),
            ),
        ),
    )
    def test_map_should_add_dynamic_path(
        self,
        router: urls.Router[str],
        registered_path: str,
        request_path: str,
        params: urls.PathParams,
    ) -> None:
        router.map(urls.Path(registered_path), HTTPMethod.GET, "Hello world!")
        assert router.match(urls.Path(request_path), HTTPMethod.GET) == Ok(
            urls.RouteMatch("Hello world!", params)
        )

    def test_map_should_add_head_method_for_get_mapping(
        self, router: urls.Router[str]
    ) -> None:
        router.map(urls.Path("/"), HTTPMethod.GET, "Hello world!")
        assert router.match(urls.Path("/"), HTTPMethod.HEAD) == Ok(
            urls.RouteMatch("Hello world!", colls.Map())
        )

    def test_map_should_add_path_for_multiple_methods(
        self, router: urls.Router[str]
    ) -> None:
        methods = [HTTPMethod.GET, HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.DELETE]
        router.map(
            urls.Path("/"),
            methods,
            "Hello world!",
        )
        for m in methods:
            assert router.match(urls.Path("/"), m) == Ok(
                urls.RouteMatch("Hello world!", colls.Map())
            )

    # ===============match==============
    def test_match_should_return_not_found_err_if_path_not_in_router(
        self, router: urls.Router[str]
    ) -> None:
        router.map(urls.Path("/"), HTTPMethod.GET, "Hello world!")
        assert router.match(urls.Path("/hello"), HTTPMethod.GET) == Err(
            urls.NotFoundErr(urls.Path("/hello"))
        )

    def test_match_should_return_method_not_allowed_err_if_method_not_registered(
        self, router: urls.Router[str]
    ) -> None:
        router.map(urls.Path("/"), HTTPMethod.POST, "Hello world!")
        assert router.match(urls.Path("/"), HTTPMethod.GET) == Err(
            urls.MethodNotAllowedErr(urls.Path("/"), HTTPMethod.GET, [HTTPMethod.POST])
        )
