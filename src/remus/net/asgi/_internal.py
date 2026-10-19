import asyncio
import mimetypes
import os
import pathlib
import urllib.parse
import uuid
from collections.abc import AsyncGenerator, AsyncIterator, Callable, Iterable
from dataclasses import dataclass

import aiofiles.os
import asgiref.typing as asgiref

from remus import Maybe, Nothing, Some, colls, panic
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
type Middleware = Callable[[asgiref.ASGI3Application], asgiref.ASGI3Application]


# ==========================================
# ===            Apps                 ===
# ==========================================
class App:
    def __init__(self) -> None:
        self._app: asgiref.ASGI3Application = self.__app__
        self._router: urls.Router[Mount] = urls.Router()

    def delete(self, path: str) -> http.Middleware:
        return self.route(path, http.Method.DELETE)

    def get(self, path: str) -> http.Middleware:
        return self.route(path, http.Method.GET)

    def mount(self, path: str, app: asgiref.ASGI3Application) -> None:
        mount = Mount(urls.Path(path), app)
        self._router.map(urls.Path(f"/{path}/*"), http.Method, mount)

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
            mount = Mount(urls.Path(""), HTTPHandlerApp(handler))
            self._router.map(urls.Path(path), methods, mount)
            return handler

        return decorator

    def use(self, middleware: Middleware) -> None:
        self._app = middleware(self._app)

    def websocket(self, path: str) -> ws.Middleware:
        def decorator(handler: ws.Handler) -> ws.Handler:
            mount = Mount(urls.Path(""), WSHandlerApp(handler))
            self._router.map(urls.Path(path), http.Method.GET, mount)
            return handler

        return decorator

    async def __app__(
        self,
        scope: asgiref.Scope,
        receive: asgiref.ASGIReceiveCallable,
        send: asgiref.ASGISendCallable,
    ) -> None:
        await RouterApp(self._router)(scope, receive, send)

    async def __call__(
        self,
        scope: asgiref.Scope,
        receive: asgiref.ASGIReceiveCallable,
        send: asgiref.ASGISendCallable,
    ) -> None:
        try:
            await self._app(scope, receive, send)

        except Panic as e:
            response = http.error(http.Status.INTERNAL_SERVER_ERROR)
            await ResponseApp(response)(scope, receive, send)

            panic_excepthook(e.__class__, e, e.__traceback__)


class HTTPHandlerApp:
    def __init__(self, handler: http.Handler) -> None:
        self._handler = handler

    async def __call__(
        self,
        scope: asgiref.Scope,
        receive: asgiref.ASGIReceiveCallable,
        send: asgiref.ASGISendCallable,
    ) -> None:
        request = new_http_request(scope, receive, send)
        response = await self._handler(request)
        await ResponseApp(response)(scope, receive, send)


@dataclass(frozen=True, slots=True)
class Mount:
    path: urls.Path
    app: asgiref.ASGI3Application


class ResponseApp:
    def __init__(self, response: http.Response) -> None:
        self._response = response

    async def __call__(
        self,
        scope: asgiref.Scope,
        receive: asgiref.ASGIReceiveCallable,
        send: asgiref.ASGISendCallable,
    ) -> None:
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

    async def _send_bytes(
        self, send: asgiref.ASGISendCallable, body: bytes, *, more_body: bool
    ) -> None:
        await send({"type": "http.response.body", "body": body, "more_body": more_body})

    async def _send_str(
        self, send: asgiref.ASGISendCallable, body: str, *, more_body: bool
    ) -> None:
        await self._send_bytes(send, body.encode("utf-8"), more_body=more_body)

    async def _send_file(
        self, scope: asgiref.Scope, send: asgiref.ASGISendCallable, file: http.File
    ) -> None:
        if "http.response.pathsend" in (scope.get("extensions") or {}):
            return await send(
                {"type": "http.response.pathsend", "path": str(file.path)}  # type: ignore
            )

        async def stream_iter() -> AsyncGenerator[bytes]:
            async with aiofiles.open(file.path, "rb") as f:
                while chunk := await f.read(SEND_FILE_CHUNK_SIZE):
                    yield chunk

        await self._send_stream(send, http.Stream(stream_iter()))

    async def _send_stream(
        self, send: asgiref.ASGISendCallable, stream: http.Stream
    ) -> None:
        async for chunk in stream:
            match chunk:
                case bytes():
                    await self._send_bytes(send, chunk, more_body=True)

                case str():
                    await self._send_str(send, chunk, more_body=True)

        await self._send_none(send)

    async def _send_none(self, send: asgiref.ASGISendCallable) -> None:
        await self._send_bytes(send, b"", more_body=False)


class RouterApp:
    def __init__(self, router: urls.Router[Mount]) -> None:
        self._router = router

    async def __call__(
        self,
        scope: asgiref.Scope,
        receive: asgiref.ASGIReceiveCallable,
        send: asgiref.ASGISendCallable,
    ) -> None:
        if scope["type"] == "lifespan":
            return

        path = urls.Path(scope["path"])
        method = http.Method(scope.get("method") or http.Method.GET)

        route_match = self._router.match(path, method).value

        match route_match:
            case urls.RouteMatch():
                mount = route_match.target
                mounted_scope = scope.copy()
                mounted_scope.get("state", {})["path_params"] = route_match.params
                mounted_scope["path"] = urls.Path(path.removeprefix(mount.path))
                mounted_scope["root_path"] = urls.Path(
                    f"{scope['root_path']}/{mount.path}"
                )
                await mount.app(mounted_scope, receive, send)

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


class StaticFilesApp:
    def __init__(self, static_dir: str | os.PathLike[str]) -> None:
        self._static_dir = pathlib.Path(static_dir).resolve()

    async def __call__(
        self,
        scope: asgiref.Scope,
        receive: asgiref.ASGIReceiveCallable,
        send: asgiref.ASGISendCallable,
    ) -> None:
        if scope["type"] != "http":
            return

        path = pathlib.Path(f"{self._static_dir}/{scope['path']}").resolve()

        if path.is_file():
            response = http.file(http.Status.OK, path)

        else:
            response = http.error(http.Status.NOT_FOUND)

        await ResponseApp(response)(scope, receive, send)


class WSHandlerApp:
    def __init__(self, handler: ws.Handler) -> None:
        self._handler = handler

    async def __call__(
        self,
        scope: asgiref.Scope,
        receive: asgiref.ASGIReceiveCallable,
        send: asgiref.ASGISendCallable,
    ) -> None:
        request = new_ws_request(scope, receive, send)

        async for message in self._handler(request):
            await WSMessageApp(message)(scope, receive, send)

            if isinstance(message, ws.Close):
                break


class WSMessageApp:
    def __init__(self, message: ws.Message) -> None:
        self._message = message

    async def __call__(
        self,
        scope: asgiref.Scope,
        receive: asgiref.ASGIReceiveCallable,
        send: asgiref.ASGISendCallable,
    ) -> None:
        if scope["type"] != "websocket":
            return

        message = self._message

        match message:
            case bytes():
                await send({"type": "websocket.send", "bytes": message, "text": None})

            case str():
                await send({"type": "websocket.send", "text": message, "bytes": None})

            case ws.Close():
                try:
                    await send(
                        {
                            "type": "websocket.close",
                            "code": message.code,
                            "reason": message.reason,
                        }
                    )

                except OSError:
                    pass


# ==========================================
# ===            Factories                 ===
# ==========================================
class BodyFactory:
    def __init__(self, receive: asgiref.ASGIReceiveCallable) -> None:
        self._receive = receive

        self._body: bytes | None = None
        self._stream_consumed: bool = False

    def __aiter__(self) -> AsyncIterator[bytes]:
        return self._body_iter()

    async def __call__(self) -> bytes:
        return b"".join([chunk async for chunk in self])

    async def _body_iter(self) -> AsyncGenerator[bytes]:
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


class HeadersFactory:
    def __init__(self, asgi_headers: Iterable[tuple[bytes, bytes]]) -> None:
        self._asgi_headers = asgi_headers

        self._headers: urls.Headers | None = None

    def __call__(self) -> urls.Headers:
        if self._headers is None:
            headers_dict: dict[str, list[str]] = {}
            for k, v in self._asgi_headers:
                key = k.decode("latin-1")
                value = v.decode("latin-1")
                headers_dict.setdefault(key, []).append(value)
            self._headers = urls.Headers(headers_dict)
        return self._headers


class QueriesFactory:
    def __init__(self, query_string: bytes) -> None:
        self._query_string = query_string

        self._queries: urls.Queries | None = None

    def __call__(self) -> urls.Queries:
        if self._queries is None:
            query_str = self._query_string.decode("latin-1")
            query_dict = urllib.parse.parse_qs(query_str, keep_blank_values=True)
            self._queries = urls.Queries(query_dict)
        return self._queries


# ==========================================
# ===            Handlers                 ===
# ==========================================
class AppHTTPHandler:
    def __init__(self, app: asgiref.ASGI3Application) -> None:
        self._app = app

    async def __call__(self, request: http.Request) -> http.Response:
        metadata: RequestMetadata = request.metadata.get(REQUEST_METADATA_KEY).expect(
            "expected RequestMetadata to be present"
        )

        scope = metadata.scope
        receive = metadata.receive

        status: Maybe[http.Status] = Nothing
        headers: Maybe[urls.MutHeaders] = Nothing
        body_queue: asyncio.Queue[asgiref.HTTPResponseBodyEvent] = asyncio.Queue()

        start = asyncio.Event()

        async def send_wrapper(
            event: asgiref.ASGISendEvent,
        ) -> None:
            nonlocal status, headers

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
        return urls.MutHeaders(headers_dict)


class AppWSHandler:
    def __init__(self, app: asgiref.ASGI3Application) -> None:
        self._app = app

    def __call__(self, request: ws.Request) -> AsyncGenerator[ws.Message]:
        return self._message_iter(request)

    async def _message_iter(self, request: ws.Request) -> AsyncGenerator[ws.Message]:
        metadata: RequestMetadata = request.metadata.get(REQUEST_METADATA_KEY).expect(
            "expected RequestMetadata to be present"
        )

        scope = metadata.scope
        receive = metadata.receive
        send = metadata.send

        message_queue: asyncio.Queue[ws.Message] = asyncio.Queue()

        start = asyncio.Event()

        async def send_wrapper(
            event: asgiref.ASGISendEvent,
        ) -> None:

            if event["type"] == "websocket.accept":
                await send(event)
                start.set()

            if event["type"] == "websocket.send":
                if data := event.get("bytes"):
                    await message_queue.put(data)

                if data := event.get("text"):
                    await message_queue.put(data)

            if event["type"] == "websocket.close":
                await send(event)
                code = ws.Code(event["code"])
                reason = event.get("reason") or ""
                await message_queue.put(ws.Close(code, reason))

        async def app_task() -> None:
            await self._app(scope, receive, send_wrapper)

        asyncio.create_task(app_task())
        await start.wait()

        while True:
            message = await message_queue.get()
            yield message

            if isinstance(message, ws.Close):
                break


# ==========================================
# ===            Middleware                 ===
# ==========================================
class HTTPMiddleware:
    def __init__(self, middleware: http.Middleware) -> None:
        self._middleware = middleware

    def __call__(self, app: asgiref.ASGI3Application) -> asgiref.ASGI3Application:
        async def wrapper(
            scope: asgiref.Scope,
            receive: asgiref.ASGIReceiveCallable,
            send: asgiref.ASGISendCallable,
        ) -> None:
            if scope["type"] != "http":
                return await app(scope, receive, send)

            handler = self._middleware(AppHTTPHandler(app))
            await HTTPHandlerApp(handler)(scope, receive, send)

        return wrapper


class WSMiddleware:
    def __init__(self, middleware: ws.Middleware) -> None:
        self._middleware = middleware

    def __call__(self, app: asgiref.ASGI3Application) -> asgiref.ASGI3Application:
        async def wrapper(
            scope: asgiref.Scope,
            receive: asgiref.ASGIReceiveCallable,
            send: asgiref.ASGISendCallable,
        ) -> None:
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
    scope: asgiref.Scope
    receive: asgiref.ASGIReceiveCallable
    send: asgiref.ASGISendCallable


class WSRequestContext:
    def __init__(
        self,
        receive: asgiref.ASGIReceiveCallable,
        send: asgiref.ASGISendCallable,
    ) -> None:
        self._receive = receive
        self._send = send

        self._is_upgraded: bool = False

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

        return ws.Websocket(WebsocketContext(self._receive))


def new_http_request(
    scope: asgiref.Scope,
    receive: asgiref.ASGIReceiveCallable,
    send: asgiref.ASGISendCallable,
) -> http.Request:
    if scope["type"] != "http":
        panic(f"expected ASGI scope type 'http', got {scope['type']!r}")

    return http.Request(
        path=urls.Path(scope["path"]),
        params=scope.get("state", {}).get("path_params", colls.Map()),
        method=http.Method(scope["method"]),
        headers_factory=HeadersFactory(scope["headers"]),
        queries_factory=QueriesFactory(scope["query_string"]),
        metadata={REQUEST_METADATA_KEY: RequestMetadata(scope, receive, send)},
        body_factory=BodyFactory(receive),
    )


def new_ws_request(
    scope: asgiref.Scope,
    receive: asgiref.ASGIReceiveCallable,
    send: asgiref.ASGISendCallable,
) -> ws.Request:
    if scope["type"] != "websocket":
        panic(f"expected ASGI scope type 'websocket', got {scope['type']!r}")

    return ws.Request(
        path=urls.Path(scope["path"]),
        params=scope.get("state", {}).get("path_params", colls.Map()),
        method=http.Method.GET,
        headers_factory=HeadersFactory(scope["headers"]),
        queries_factory=QueriesFactory(scope["query_string"]),
        metadata={REQUEST_METADATA_KEY: RequestMetadata(scope, receive, send)},
        context=WSRequestContext(receive, send),
    )


# ==========================================
# ===            Websockets                 ===
# ==========================================
class WebsocketContext:
    def __init__(self, receive: asgiref.ASGIReceiveCallable) -> None:
        self._receive = receive

    def __aiter__(self) -> AsyncIterator[ws.Message]:
        return self._message_iter()

    async def _message_iter(self) -> AsyncGenerator[ws.Message]:
        while True:
            event = await self._receive()

            if event["type"] == "websocket.disconnect":
                code = ws.Code(event["code"])
                reason = event.get("reason") or ""
                yield ws.Close(code, reason)
                break

            if event["type"] != "websocket.receive":
                break

            data = event.get("bytes") or event.get("text")

            if data is None:
                break

            yield data
