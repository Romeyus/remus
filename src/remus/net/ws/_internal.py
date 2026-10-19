from collections.abc import AsyncGenerator, AsyncIterator, Callable, Mapping
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Protocol, override

from remus import Err, Ok, Result
from remus.net import http, urls
from remus.net.http._internal import BaseRequest


# ==========================================
# ===            Constants                 ===
# ==========================================
class Code(IntEnum):
    NORMAL_CLOSURE = 1000
    GOING_AWAY = 1001
    PROTOCOL_ERROR = 1002
    UNSUPPORTED_DATA = 1003
    RESERVED = 1004
    NO_STATUS_RECEIVED = 1005
    ABNORMAL_CLOSURE = 1006
    INVALID_PAYLOAD_DATA = 1007
    POLICY_VIOLATION = 1008
    MESSAGE_TOO_BIG = 1009
    MANDATORY_EXTENSION = 1010
    INTERNAL_ERROR = 1011
    SERVICE_RESTART = 1012
    TRY_AGAIN_LATER = 1013
    BAD_GATEWAY = 1014
    TLS_HANDSHAKE = 1015

    @property
    def phrase(self) -> str:
        return {
            1000: "Normal Closure",
            1001: "Going Away",
            1002: "Protocol Error",
            1003: "Unsupported Data",
            1004: "Reserved",
            1005: "No Status Received",
            1006: "Abnormal Closure",
            1007: "Invalid Payload Data",
            1008: "Policy Violation",
            1009: "Message Too Big",
            1010: "Mandatory Extension",
            1011: "Internal Error",
            1012: "Service Restart",
            1013: "Try Again Later",
            1014: "Bad Gateway",
            1015: "TLS Handshake",
        }[self]


# ==========================================
# ===            Types                 ===
# ==========================================
type Handler = Callable[[Request], AsyncGenerator[Message]]
type Message = bytes | str | Close
type Middleware = Callable[[Handler], Handler]


class RequestContext(Protocol):
    async def upgrade(self) -> Websocket: ...


class WebsocketContext(Protocol):
    def __aiter__(self) -> AsyncIterator[Message]: ...


# ==========================================
# ===            Closures                 ===
# ==========================================
@dataclass(frozen=True, slots=True)
class Close:
    code: Code = Code.NORMAL_CLOSURE
    reason: str = ""

    def __post_init__(self) -> None:
        if not self.reason:
            object.__setattr__(self, "reason", self.code.phrase)


# ==========================================
# ===            Requests                 ===
# ==========================================
class Request(BaseRequest):
    @override
    def __init__(
        self,
        *,
        path: urls.Path,
        params: urls.PathParams,
        method: http.Method,
        headers_factory: Callable[[], urls.Headers],
        queries_factory: Callable[[], urls.Queries],
        metadata: Mapping[str, Any],
        context: RequestContext,
    ) -> None:
        super().__init__(
            path=path,
            params=params,
            method=method,
            headers_factory=headers_factory,
            queries_factory=queries_factory,
            metadata=metadata,
        )

        self._context = context

    async def upgrade(self) -> Websocket:
        return await self._context.upgrade()


# ==========================================
# ===            Websockets                 ===
# ==========================================
class Websocket:
    def __init__(self, context: WebsocketContext) -> None:
        self._context = context

    def as_bytes(self) -> AsyncIterator[Result[bytes, Close]]:
        async def wrapper() -> AsyncGenerator[Result[bytes, Close]]:
            async for message in self:
                if isinstance(message, bytes):
                    yield Ok(message)

                else:
                    yield Err(Close(Code.UNSUPPORTED_DATA))

        return wrapper()

    def as_str(self) -> AsyncIterator[Result[str, Close]]:
        async def wrapper() -> AsyncGenerator[Result[str, Close]]:
            async for message in self:
                if isinstance(message, str):
                    yield Ok(message)

                else:
                    yield Err(Close(Code.UNSUPPORTED_DATA))

        return wrapper()

    def __aiter__(self) -> AsyncIterator[Message]:
        return aiter(self._context)
