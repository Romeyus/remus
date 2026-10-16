from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from http import HTTPMethod

from remus import Err, Ok, Result, panic

try:
    import nanoroute

except ImportError:  # pragma: no cover
    panic("missing dependency, install 'remus[net]'")

# ==========================================
# ===            Types                 ===
# ==========================================
type PathParams = Mapping[str, str]
type RouteErr = NotFoundErr | MethodNotAllowedErr


# ==========================================
# ===            Routing                 ===
# ==========================================
@dataclass(frozen=True, slots=True)
class Path:
    value: str

    def __post_init__(self) -> None:
        if ".." in self.value:
            panic(
                f"path contains '..', navigating to parent directories is forbidden, {self.value}"
            )

        parts = [p for p in self.value.split("/") if p]
        normalised = "/".join(parts)
        object.__setattr__(self, "value", f"/{normalised}")


@dataclass(frozen=True, slots=True)
class RouteMatch[T]:
    target: T
    params: PathParams


@dataclass(frozen=True, slots=True)
class Router[T]:
    _nanorouter: nanoroute.router = field(default_factory=nanoroute.router, init=False)

    def map(
        self, path: Path, methods: HTTPMethod | Iterable[HTTPMethod], target: T
    ) -> None:
        if isinstance(methods, HTTPMethod):
            all_methods = {methods}
        else:
            all_methods = set(methods)

        if HTTPMethod.GET in all_methods:
            all_methods.add(HTTPMethod.HEAD)

        self._nanorouter.route(all_methods, path.value)(target)

    def match(self, path: Path, method: HTTPMethod) -> Result[RouteMatch[T], RouteErr]:
        try:
            target, params = self._nanorouter.lookup(method, path.value)
            return Ok(RouteMatch(target, params))

        except LookupError:
            allowed_methods: list[HTTPMethod] = []

            for m in HTTPMethod:
                try:
                    self._nanorouter.lookup(m, path.value)
                    allowed_methods.append(m)

                except LookupError:
                    continue

            if not allowed_methods:
                return Err(NotFoundErr(path))

            return Err(MethodNotAllowedErr(path, method, allowed_methods))


@dataclass(frozen=True, slots=True)
class NotFoundErr:
    path: Path


@dataclass(frozen=True, slots=True)
class MethodNotAllowedErr:
    path: Path
    method: HTTPMethod
    allowed_methods: Iterable[HTTPMethod]
