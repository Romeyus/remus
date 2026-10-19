import os
import pathlib
from abc import ABC
from collections.abc import AsyncIterable, AsyncIterator, Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from http import HTTPMethod, HTTPStatus
from typing import Any, Protocol, Self, override

from remus import Maybe, colls
from remus.net import urls

# ==========================================
# ===            Constants                 ===
# ==========================================
Method = HTTPMethod
Status = HTTPStatus

# ==========================================
# ===            Types                 ===
# ==========================================
type Body = bytes | str | File | Stream
type Handler = Callable[[Request], Awaitable[Response]]
type Middleware = Callable[[Handler], Handler]


class BodyFactory(Protocol):
    def __aiter__(self) -> AsyncIterator[bytes]: ...
    async def __call__(self) -> bytes: ...


# ==========================================
# ===            Requests                 ===
# ==========================================
class BaseRequest(ABC):
    def __init__(
        self,
        *,
        path: urls.Path,
        params: urls.PathParams,
        method: Method,
        headers_factory: Callable[[], urls.Headers],
        queries_factory: Callable[[], urls.Queries],
        metadata: Mapping[str, Any],
    ) -> None:
        self._path = path
        self._params = params
        self._method = method
        self._headers_factory = headers_factory
        self._queries_factory = queries_factory
        self._metadata = colls.Map(metadata)

    @property
    def path(self) -> str:
        return self._path

    @property
    def params(self) -> urls.PathParams:
        return self._params

    @property
    def method(self) -> Method:
        return self._method

    @property
    def headers(self) -> urls.Headers:
        return self._headers_factory()

    @property
    def queries(self) -> urls.Queries:
        return self._queries_factory()

    @property
    def metadata(self) -> colls.Map[str, Any]:
        return self._metadata


class Request(BaseRequest):
    @override
    def __init__(
        self,
        *,
        path: urls.Path,
        params: urls.PathParams,
        method: Method,
        headers_factory: Callable[[], urls.Headers],
        queries_factory: Callable[[], urls.Queries],
        metadata: Mapping[str, Any],
        body_factory: BodyFactory,
    ) -> None:
        super().__init__(
            path=path,
            params=params,
            method=method,
            headers_factory=headers_factory,
            queries_factory=queries_factory,
            metadata=metadata,
        )

        self._body_factory = body_factory

    async def body(self) -> bytes:
        return await self._body_factory()

    def stream(self) -> AsyncIterator[bytes]:
        return aiter(self._body_factory)


# ==========================================
# ===            Responses                 ===
# ==========================================
@dataclass(slots=True)
class Response:
    status: Status
    body: Body | None = None
    headers: urls.MutHeaders = field(default_factory=urls.MutHeaders)

    @property
    def content_type(self) -> Maybe[str]:
        return self.headers.get("content-type")

    def append_header(self, key: str, value: str) -> Self:
        self.headers.append(key, value)
        return self

    def set_content_type(self, value: str) -> Self:
        return self.set_header("content-type", value)

    def set_header(self, key: str, value: str) -> Self:
        self.headers.set(key, value)
        return self

    def set_status(self, value: Status) -> Self:
        self.status = value
        return self


class File:
    def __init__(self, path: str | os.PathLike[str]) -> None:
        self._path = pathlib.Path(path).resolve()

    @property
    def path(self) -> pathlib.Path:
        return self._path

    def __str__(self) -> str:
        return str(self._path)


class Stream:
    def __init__(self, async_iterable: AsyncIterable[bytes | str]) -> None:
        self._aiter = async_iterable

    def __aiter__(self) -> AsyncIterator[bytes | str]:
        return aiter(self._aiter)


def text(status: Status, content: bytes | str) -> Response:
    return Response(status, content).set_content_type("text/plain; charset=utf-8")


def html(status: Status, content: bytes | str) -> Response:
    return Response(status, content).set_content_type("text/html; charset=utf-8")


def file(status: Status, path: str) -> Response:
    return Response(status, File(pathlib.Path(path)))


def stream(status: Status, async_iterable: AsyncIterable[bytes | str]) -> Response:
    return Response(status, Stream(async_iterable))


def sse(status: Status, async_iterable: AsyncIterable[bytes | str]) -> Response:
    return (
        stream(status, async_iterable)
        .set_content_type("text/event-stream")
        .set_header("cache-control", "no-cache")
    )


def error(status: Status, message: str | None = None) -> Response:
    return text(status, message or status.phrase)
