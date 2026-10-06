from collections.abc import Callable
from typing import Literal, Protocol

from remus import Array, Map
from remus.net import url

type Method = Literal[
    "CONNECT", "DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT", "TRACE"
]
type Headers = Map[str, Array[str]]
type Queries = Map[str, Array[str]]


# ==========================================
# ===            Request                 ===
# ==========================================
class Request(Protocol):
    @property
    def path(self) -> url.Path: ...
    @property
    def method(self) -> Method: ...
    @property
    def headers(self) -> Headers: ...
    @property
    def queries(self) -> Queries: ...


class _Request:
    __slots__ = (
        "_headers",
        "_headers_factory",
        "_method",
        "_path",
        "_path_factory",
        "_queries",
        "_queries_factory",
    )

    def __init__(
        self,
        path_factory: Callable[[], url.Path],
        method: Method,
        headers_factory: Callable[[], Headers],
        queries_factory: Callable[[], Queries],
    ) -> None:
        self._path_factory = path_factory
        self._method: Method = method
        self._headers_factory = headers_factory
        self._queries_factory = queries_factory

        self._path: url.Path | None = None
        self._headers: Headers | None = None
        self._queries: Queries | None = None

    @property
    def path(self) -> url.Path:
        if self._path is None:
            self._path = self._path_factory()
        return self._path

    @property
    def method(self) -> Method:
        return self._method

    @property
    def headers(self) -> Headers:
        if self._headers is None:
            self._headers = self._headers_factory()
        return self._headers

    @property
    def queries(self) -> Queries:
        if self._queries is None:
            self._queries = self._queries_factory()
        return self._queries


def new_request(
    path_factory: Callable[[], url.Path],
    method: Method,
    headers_factory: Callable[[], Headers],
    queries_factory: Callable[[], Queries],
) -> Request:
    return _Request(path_factory, method, headers_factory, queries_factory)
