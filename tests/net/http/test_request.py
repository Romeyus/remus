import pytest

from remus import Array, Map
from remus.net import http, url


@pytest.fixture
def req() -> http.Request:
    return http.new_request(
        lambda: url.Path("/hello/world"),
        "GET",
        lambda: Map({"content-type": Array(["text/html"])}),
        lambda: Map({"search": Array(["hello"]), "order_by": Array(["desc"])}),
    )


def test_path(req: http.Request) -> None:
    assert req.path == "/hello/world"


def test_method(req: http.Request) -> None:
    assert req.method == "GET"


def test_headers(req: http.Request) -> None:
    assert req.headers == Map({"content-type": Array(["text/html"])})


def test_queries(req: http.Request) -> None:
    assert req.queries == Map({"search": Array(["hello"]), "order_by": Array(["desc"])})
