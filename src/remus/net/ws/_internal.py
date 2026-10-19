from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import IntEnum
from typing import Protocol

from remus import Result
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
type Handler = Callable[[Request], Awaitable[Closure]]
type Middleware = Callable[[Handler], Handler]


class RequestContext(Protocol):
    async def upgrade(self) -> Websocket: ...


class WebsocketContext(Protocol):
    async def receive_bytes(self) -> Result[bytes, Closure]: ...
    async def receive_str(self) -> Result[str, Closure]: ...
    async def send_bytes(self, data: bytes) -> None: ...
    async def send_str(self, data: str) -> None: ...


# ==========================================
# ===            Closures                 ===
# ==========================================
@dataclass(frozen=True, slots=True)
class Closure:
    code: Code
    reason: str


def close(code: Code = Code.NORMAL_CLOSURE, reason: str | None = None) -> Closure:
    return Closure(code, reason or code.phrase)


# ==========================================
# ===            Requests                 ===
# ==========================================
@dataclass(frozen=True, slots=True)
class Request(BaseRequest):
    _context: RequestContext

    async def upgrade(self) -> Websocket:
        return await self._context.upgrade()


# ==========================================
# ===            Websockets                 ===
# ==========================================
@dataclass(frozen=True, slots=True)
class Websocket:
    _context: WebsocketContext

    async def receive_bytes(self) -> Result[bytes, Closure]:
        return await self._context.receive_bytes()

    async def receive_str(self) -> Result[str, Closure]:
        return await self._context.receive_str()

    async def send_bytes(self, data: bytes) -> None:
        await self._context.send_bytes(data)

    async def send_str(self, data: str) -> None:
        await self._context.send_str(data)
