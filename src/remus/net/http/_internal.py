import os
import pathlib
from abc import ABC
from collections.abc import AsyncIterable, AsyncIterator, Awaitable, Callable
from dataclasses import dataclass, field
from http import HTTPMethod, HTTPStatus
from typing import Protocol, Self

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
type HeadersFactory = Callable[[], urls.Headers]
type Middleware = Callable[[Handler], Handler]
type QueriesFactory = Callable[[], urls.Queries]


class BodyFactory(Protocol):
    def __aiter__(self) -> AsyncIterator[bytes]: ...
    async def __call__(self) -> bytes: ...


# ==========================================
# ===            Requests                 ===
# ==========================================
@dataclass(frozen=True, slots=True)
class BaseRequest(ABC):
    _path: urls.Path
    params: urls.PathParams
    method: Method
    _headers_factory: HeadersFactory
    _queries_factory: QueriesFactory

    @property
    def path(self) -> str:
        return self._path.value

    @property
    def headers(self) -> urls.Headers:
        return self._headers_factory()

    @property
    def queries(self) -> urls.Queries:
        return self._queries_factory()


@dataclass(frozen=True, slots=True)
class Request(BaseRequest):
    _body_factory: BodyFactory

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

    def append_header(self, key: str, value: str) -> Self:
        self.headers.append(key, value)
        return self

    def pop_header(self, key: str) -> Self:
        self.headers.pop(key)
        return self

    def set_content_type(self, value: str) -> Self:
        return self.set_header("content-type", value)

    def set_header(self, key: str, value: str) -> Self:
        self.headers.set(key, value)
        return self

    def set_status(self, value: Status) -> Self:
        self.status = value
        return self


@dataclass(frozen=True, slots=True)
class File:
    path: os.PathLike[str]

    def __post_init__(self) -> None:
        object.__setattr__(self, "path", pathlib.Path(self.path).resolve())


@dataclass(frozen=True, slots=True)
class Stream:
    _aiter: AsyncIterable[bytes | str]

    def __aiter__(self) -> AsyncIterator[bytes | str]:
        return aiter(self._aiter)


def text(status: Status, content: bytes | str) -> Response:
    return Response(status, content).set_content_type("text/plain")


def html(status: Status, content: bytes | str) -> Response:
    return Response(status, content).set_content_type("text/html; charset=utf-8")


def file(status: Status, path: str) -> Response:
    return Response(status, File(pathlib.Path(path)))


def stream(status: Status, aiter: AsyncIterable[bytes | str]) -> Response:
    return Response(status, Stream(aiter))


def sse(status: Status, aiter: AsyncIterable[bytes | str]) -> Response:
    return (
        stream(status, aiter)
        .set_content_type("text/event-stream")
        .set_header("cache-control", "no-cache")
    )
