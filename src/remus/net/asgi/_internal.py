import asyncio
import mimetypes
import urllib.parse
import uuid
from collections.abc import AsyncGenerator, AsyncIterator, Callable, Iterable
from dataclasses import dataclass, field

import aiofiles.os
import asgiref.typing as asgiref

from remus import Err, Maybe, Nothing, Ok, Some, colls, panic, strs
from remus._internal import Panic, panic_excepthook
from remus.net import http, urls

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

    async def __app__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return

        path = urls.Path(scope["path"])
        method = http.Method(scope["method"])

        match_res = self._router.match(path, method)

        match match_res:
            case Ok():
                route_match = match_res.value
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

            case Err():
                route_err = match_res.value

                match route_err:
                    case urls.NotFoundErr():
                        response = http.error(http.Status.NOT_FOUND)

                    case urls.MethodNotAllowedErr():
                        if route_err.method == http.Method.OPTIONS:
                            response = http.Response(http.Status.OK)

                        else:
                            response = http.Response(http.Status.METHOD_NOT_ALLOWED)

                        response.set_header(
                            "allow", ", ".join(route_err.allowed_methods)
                        )

                await ResponseApp(response)(scope, receive, send)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        try:
            await self._app(scope, receive, send)

        except Panic as e:
            response = http.error(http.Status.INTERNAL_SERVER_ERROR)
            await ResponseApp(response)(scope, receive, send)

            panic_excepthook(e.__class__, e, e.__traceback__)


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

        status: Maybe[http.Status] = Nothing
        headers: Maybe[urls.MutHeaders] = Nothing
        body_queue: asyncio.Queue[asgiref.HTTPResponseBodyEvent] = asyncio.Queue()

        start = asyncio.Event()

        async def send_wrapper(event: asgiref.ASGISendEvent) -> None:
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

        headers_map = colls.MutMap(
            {strs.Lowercase(k): colls.MutArray(v) for k, v in headers_dict.items()}
        )
        return urls.MutHeaders(headers_map)


# ==========================================
# ===            Middleware                 ===
# ==========================================
@dataclass(frozen=True, slots=True)
class HTTPMiddleware:
    _middleware: http.Middleware

    def __call__(self, app: Application) -> Application:
        async def wrapper(scope: Scope, receive: Receive, send: Send) -> None:
            if scope["type"] != "http":
                return

            handler = self._middleware(AppHTTPHandler(app))
            await HTTPHandlerApp(handler)(scope, receive, send)

        return wrapper


# ==========================================
# ===            Requests                 ===
# ==========================================
@dataclass(frozen=True, slots=True)
class RequestMetadata:
    scope: Scope
    receive: Receive


def new_http_request(scope: Scope, receive: Receive, send: Send) -> http.Request:
    if scope["type"] != "http":
        panic(f"expected ASGI scope type 'http', got {scope['type']!r}")

    return http.Request(
        urls.Path(scope["path"]),
        scope.get("state", {}).get("path_params", colls.Map()),
        http.Method(scope["method"]),
        HeadersFactory(scope["headers"]),
        QueriesFactory(scope["query_string"]),
        colls.MutMap({REQUEST_METADATA_KEY: RequestMetadata(scope, receive)}),
        BodyFactory(receive),
    )
