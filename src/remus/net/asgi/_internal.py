import asyncio
import mimetypes
import urllib.parse
import uuid
from collections.abc import AsyncGenerator, AsyncIterator, Callable, Iterable
from dataclasses import dataclass, field

import aiofiles.os
import asgiref.typing as asgiref

from remus import Err, Maybe, Nothing, Ok, Result, Some, colls, panic, strs
from remus._internal import Panic, panic_excepthook
from remus.net import http, urls, ws

# ==========================================
# ===            Constants                 ===
# ==========================================
REQUEST_METADATA_KEY = str(uuid.uuid4())
SEND_FILE_CHUNK_SIZE = 1024

# ==========================================
# ===            Types                 ===
# ==========================================
type Application = asgiref.ASGI3Application
type Middleware = Callable[[Application], Application]
type Mount = tuple[urls.Path, Application]
type Receive = asgiref.ASGIReceiveCallable
type Scope = asgiref.Scope
type Send = asgiref.ASGISendCallable


# ==========================================
# ===            Apps                 ===
# ==========================================
class App:
    def __init__(self) -> None:
        self._app: Application = self.__app__
        self._router: urls.Router[Mount] = urls.Router()

    def delete(self, path: str) -> http.Middleware:
        return self.route(path, http.Method.DELETE)

    def get(self, path: str) -> http.Middleware:
        return self.route(path, http.Method.GET)

    def mount(self, path: str, app: Application) -> None:
        self._router.map(urls.Path(path), http.Method, (urls.Path(path), app))

    def patch(self, path: str) -> http.Middleware:
        return self.route(path, http.Method.PATCH)

    def post(self, path: str) -> http.Middleware:
        return self.route(path, http.Method.POST)

    def put(self, path: str) -> http.Middleware:
        return self.route(path, http.Method.PUT)

    def route(
        self, path: str, methods: http.Method | Iterable[http.Method]
    ) -> http.Middleware:
        def decorator(handler: http.Handler) -> http.Handler:
            target = urls.Path(path), HTTPHandlerApp(handler)
            self._router.map(urls.Path(path), methods, target)
            return handler

        return decorator

    def use(self, middleware: Middleware) -> None:
        self._app = middleware(self._app)

    def websocket(self, path: str) -> ws.Middleware:
        def decorator(handler: ws.Handler) -> ws.Handler:
            target = urls.Path(path), WSHandlerApp(handler)
            self._router.map(urls.Path(path), http.Method.GET, target)
            return handler

        return decorator

    async def __app__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await RouterApp(self._router)(scope, receive, send)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        try:
            await self._app(scope, receive, send)

        except Panic as e:
            response = http.error(http.Status.INTERNAL_SERVER_ERROR)
            await ResponseApp(response)(scope, receive, send)

            panic_excepthook(e.__class__, e, e.__traceback__)


@dataclass(frozen=True, slots=True)
class ClosureApp:
    _closure: ws.Closure

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "websocket":
            return

        code = self._closure.code
        reason = self._closure.reason

        try:
            await send({"type": "websocket.close", "code": code, "reason": reason})

        except OSError:
            pass


@dataclass(frozen=True, slots=True)
class HTTPHandlerApp:
    _handler: http.Handler

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        request = new_http_request(scope, receive, send)
        response = await self._handler(request)
        await ResponseApp(response)(scope, receive, send)


@dataclass(frozen=True, slots=True)
class ResponseApp:
    _response: http.Response

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return

        status = self._response.status
        headers = self._response.headers
        body = self._response.body

        if isinstance(body, (bytes, str)):
            headers.set("content-length", str(len(body)))

        if isinstance(body, http.File):
            stats = await aiofiles.os.stat(body.path)
            headers.set("content-length", str(stats.st_size))

            mimetype, encoding = mimetypes.guess_file_type(body.path)

            if mimetype and encoding:
                content_type = f"{mimetype}; charset={encoding}"

            elif mimetype and not encoding:
                content_type = mimetype

            else:
                content_type = "application/octet-stream"

            headers.set("content-type", content_type)

        if status != http.Status.NO_CONTENT and body is None:
            headers.set("content-length", "0")

        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": [
                    (k.encode("latin-1"), v.encode("latin-1"))
                    for k, v in headers.items()
                ],
                "trailers": False,
            }
        )

        match body:
            case bytes():
                await self._send_bytes(send, body, more_body=False)

            case str():
                await self._send_str(send, body, more_body=False)

            case http.File():
                await self._send_file(scope, send, body)

            case http.Stream():
                await self._send_stream(send, body)

            case None:
                await self._send_none(send)

    async def _send_bytes(self, send: Send, body: bytes, *, more_body: bool) -> None:
        await send({"type": "http.response.body", "body": body, "more_body": more_body})

    async def _send_str(self, send: Send, body: str, *, more_body: bool) -> None:
        await self._send_bytes(send, body.encode("utf-8"), more_body=more_body)

    async def _send_file(self, scope: Scope, send: Send, file: http.File) -> None:
        if "http.response.pathsend" in (scope.get("extensions") or {}):
            return await send(
                {"type": "http.response.pathsend", "path": str(file.path)}  # type: ignore
            )

        async def stream_iter() -> AsyncGenerator[bytes]:
            async with aiofiles.open(file.path, "rb") as f:
                while chunk := await f.read(SEND_FILE_CHUNK_SIZE):
                    yield chunk

        await self._send_stream(send, http.Stream(stream_iter()))

    async def _send_stream(self, send: Send, stream: http.Stream) -> None:
        async for chunk in stream:
            match chunk:
                case bytes():
                    await self._send_bytes(send, chunk, more_body=True)

                case str():
                    await self._send_str(send, chunk, more_body=True)

        await self._send_none(send)

    async def _send_none(self, send: Send) -> None:
        await self._send_bytes(send, b"", more_body=False)


@dataclass(frozen=True, slots=True)
class RouterApp:
    _router: urls.Router[Mount]

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "lifespan":
            return

        path = urls.Path(scope["path"])
        method = http.Method(scope.get("method") or http.Method.GET)

        route_match = self._router.match(path, method).value

        match route_match:
            case urls.RouteMatch():
                mount_path, app = route_match.target
                mounted_scope = scope.copy()
                mounted_scope.get("state", {})["path_params"] = route_match.params
                mounted_scope["path"] = urls.Path(
                    path.value.removeprefix(mount_path.value)
                ).value
                mounted_scope["root_path"] = urls.Path(
                    f"{scope['root_path']}/{mount_path.value}"
                ).value
                await app(mounted_scope, receive, send)

            case urls.NotFoundErr():
                response = http.error(http.Status.NOT_FOUND)
                await ResponseApp(response)(scope, receive, send)

            case urls.MethodNotAllowedErr():
                if route_match.method == http.Method.OPTIONS:
                    response = http.Response(http.Status.NO_CONTENT)

                else:
                    response = http.Response(http.Status.METHOD_NOT_ALLOWED)

                response.set_header("allow", ", ".join(route_match.allowed_methods))
                await ResponseApp(response)(scope, receive, send)


@dataclass(frozen=True, slots=True)
class WSHandlerApp:
    _handler: ws.Handler

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        request = new_ws_request(scope, receive, send)
        closure = await self._handler(request)
        await ClosureApp(closure)(scope, receive, send)


# ==========================================
# ===            Factories                 ===
# ==========================================
@dataclass(slots=True)
class BodyFactory:
    _receive: Receive

    _body: bytes | None = field(default=None, init=False)
    _stream_consumed: bool = field(default=False, init=False)

    def __aiter__(self) -> AsyncIterator[bytes]:
        async def body_iter() -> AsyncGenerator[bytes]:
            if self._body is not None:
                yield self._body
                return

            if self._stream_consumed:
                panic("stream consumed")

            chunks: list[bytes] = []
            while True:
                event = await self._receive()

                if event["type"] != "http.request":
                    break

                chunk = event["body"]
                chunks.append(chunk)
                yield chunk

                if not event["more_body"]:
                    self._stream_consumed = True
                    break

            self._body = b"".join(chunks)

        return body_iter()

    async def __call__(self) -> bytes:
        return b"".join([chunk async for chunk in self])


@dataclass(slots=True)
class HeadersFactory:
    _asgi_headers: Iterable[tuple[bytes, bytes]]

    _headers: urls.Headers | None = field(default=None, init=False)

    def __call__(self) -> urls.Headers:
        if self._headers is None:
            headers_dict: dict[str, list[str]] = {}
            for k, v in self._asgi_headers:
                key = k.decode("latin-1")
                value = v.decode("latin-1")
                headers_dict.setdefault(key, []).append(value)

            headers_map = colls.Map(
                {strs.Lowercase(k): colls.Array(v) for k, v in headers_dict.items()}
            )
            self._headers = urls.Headers(headers_map)
        return self._headers


@dataclass(slots=True)
class QueriesFactory:
    _query_string: bytes

    _queries: urls.Queries | None = field(default=None, init=False)

    def __call__(self) -> urls.Queries:
        if self._queries is None:
            query_str = self._query_string.decode("latin-1")
            query_dict = urllib.parse.parse_qs(query_str, keep_blank_values=True)
            query_map = colls.Map({k: colls.Array(v) for k, v in query_dict.items()})
            self._queries = urls.Queries(query_map)
        return self._queries


# ==========================================
# ===            Handlers                 ===
# ==========================================
@dataclass(frozen=True, slots=True)
class AppHTTPHandler:
    _app: Application

    async def __call__(self, request: http.Request) -> http.Response:
        metadata: RequestMetadata = request.metadata.get(REQUEST_METADATA_KEY).expect(
            "expected RequestMetadata to be present"
        )

        scope = metadata.scope
        receive = metadata.receive
        send = metadata.send

        status: Maybe[http.Status] = Nothing
        headers: Maybe[urls.MutHeaders] = Nothing
        body_queue: asyncio.Queue[asgiref.HTTPResponseBodyEvent] = asyncio.Queue()

        start = asyncio.Event()

        async def send_wrapper(event: asgiref.ASGISendEvent) -> None:
            nonlocal status, headers

            await send(event)

            if event["type"] == "http.response.start":
                status = Some(http.Status(event["status"]))
                headers = Some(self._new_mut_headers(event["headers"]))
                start.set()

            if event["type"] == "http.response.body":
                await body_queue.put(event)

        async def body_iter() -> AsyncGenerator[bytes]:
            while True:
                event = await body_queue.get()
                yield event["body"]

                if not event["more_body"]:
                    break

        async def app_task() -> None:
            await self._app(scope, receive, send_wrapper)

        asyncio.create_task(app_task())
        await start.wait()

        return http.Response(
            status.unwrap(), http.Stream(body_iter()), headers.unwrap()
        )

    def _new_mut_headers(
        self, asgi_headers: Iterable[tuple[bytes, bytes]]
    ) -> urls.MutHeaders:
        headers_dict: dict[str, list[str]] = {}
        for k, v in asgi_headers:
            key = k.decode("latin-1")
            value = v.decode("latin-1")
            headers_dict.setdefault(key, []).append(value)

        headers_map = colls.MutMap(
            {strs.Lowercase(k): colls.MutArray(v) for k, v in headers_dict.items()}
        )
        return urls.MutHeaders(headers_map)


@dataclass(frozen=True, slots=True)
class AppWSHandler:
    _app: Application

    async def __call__(self, request: ws.Request) -> ws.Closure:
        metadata: RequestMetadata = request.metadata.get(REQUEST_METADATA_KEY).expect(
            "expected RequestMetadata to be present"
        )

        scope = metadata.scope
        receive = metadata.receive
        send = metadata.send

        code: Maybe[ws.Code] = Nothing
        reason: Maybe[str] = Nothing

        async def send_wrapper(event: asgiref.ASGISendEvent) -> None:
            nonlocal code, reason

            await send(event)

            if event["type"] == "websocket.close":
                code = Some(ws.Code(event["code"]))
                reason = Some(event.get("reason") or "")

        await self._app(scope, receive, send_wrapper)
        return ws.Closure(code.unwrap(), reason.unwrap())


# ==========================================
# ===            Middleware                 ===
# ==========================================
@dataclass(frozen=True, slots=True)
class HTTPMiddleware:
    _middleware: http.Middleware

    def __call__(self, app: Application) -> Application:
        async def wrapper(scope: Scope, receive: Receive, send: Send) -> None:
            if scope["type"] != "http":
                return await app(scope, receive, send)

            handler = self._middleware(AppHTTPHandler(app))
            await HTTPHandlerApp(handler)(scope, receive, send)

        return wrapper


@dataclass(frozen=True, slots=True)
class WSMiddleware:
    _middleware: ws.Middleware

    def __call__(self, app: Application) -> Application:
        async def wrapper(scope: Scope, receive: Receive, send: Send) -> None:
            if scope["type"] != "websocket":
                return await app(scope, receive, send)

            handler = self._middleware(AppWSHandler(app))
            await WSHandlerApp(handler)(scope, receive, send)

        return wrapper


# ==========================================
# ===            Requests                 ===
# ==========================================
@dataclass(frozen=True, slots=True)
class RequestMetadata:
    scope: Scope
    receive: Receive
    send: Send


@dataclass(slots=True)
class WSRequestContext:
    _receive: Receive
    _send: Send

    _is_upgraded: bool = field(default=False, init=False)

    async def upgrade(self) -> ws.Websocket:
        if self._is_upgraded:
            panic("request has already been upgraded to websocket")

        event = await self._receive()
        if event["type"] != "websocket.connect":
            panic(f"expected ASGI event 'websocket.connect', got {event['type']!r}")

        await self._send(
            {"type": "websocket.accept", "headers": [], "subprotocol": None}
        )
        self._is_upgraded = True

        return ws.Websocket(WebsocketContext(self._receive, self._send))


def new_http_request(scope: Scope, receive: Receive, send: Send) -> http.Request:
    if scope["type"] != "http":
        panic(f"expected ASGI scope type 'http', got {scope['type']!r}")

    return http.Request(
        urls.Path(scope["path"]),
        scope.get("state", {}).get("path_params", colls.Map()),
        http.Method(scope["method"]),
        HeadersFactory(scope["headers"]),
        QueriesFactory(scope["query_string"]),
        colls.MutMap({REQUEST_METADATA_KEY: RequestMetadata(scope, receive, send)}),
        BodyFactory(receive),
    )


def new_ws_request(scope: Scope, receive: Receive, send: Send) -> ws.Request:
    if scope["type"] != "websocket":
        panic(f"expected ASGI scope type 'websocket', got {scope['type']!r}")

    return ws.Request(
        urls.Path(scope["path"]),
        scope.get("state", {}).get("path_params", colls.Map()),
        http.Method.GET,
        HeadersFactory(scope["headers"]),
        QueriesFactory(scope["query_string"]),
        colls.MutMap({REQUEST_METADATA_KEY: RequestMetadata(scope, receive, send)}),
        WSRequestContext(receive, send),
    )


# ==========================================
# ===            Websockets                 ===
# ==========================================
@dataclass(frozen=True, slots=True)
class WebsocketContext:
    _receive: Receive
    _send: Send

    async def receive_bytes(self) -> Result[bytes, ws.Closure]:
        event = await self._receive()

        if event["type"] == "websocket.disconnect":
            return Err(ws.close())

        if event["type"] != "websocket.receive":
            return Err(ws.close(ws.Code.INTERNAL_ERROR))

        data = event.get("bytes")

        if data is None:
            return Err(ws.close(ws.Code.UNSUPPORTED_DATA))

        return Ok(data)

    async def receive_str(self) -> Result[str, ws.Closure]:
        event = await self._receive()

        if event["type"] == "websocket.disconnect":
            return Err(ws.close(ws.Code(event["code"]), event.get("reason")))

        if event["type"] != "websocket.receive":
            return Err(ws.close(ws.Code.INTERNAL_ERROR))

        data = event.get("text")

        if data is None:
            return Err(ws.close(ws.Code.UNSUPPORTED_DATA))

        return Ok(data)

    async def send_bytes(self, data: bytes) -> None:
        await self._send({"type": "websocket.send", "bytes": data, "text": None})

    async def send_str(self, data: str) -> None:
        await self._send({"type": "websocket.send", "text": data, "bytes": None})
