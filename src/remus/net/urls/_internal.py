from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from http import HTTPMethod

from remus import Err, Maybe, Ok, Result, colls, errs, panic, strs

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


# ==========================================
# ===            URL Values                 ===
# ==========================================
@dataclass(frozen=True, slots=True)
class Cookies:
    map: colls.Map[str, colls.Array[str]] = field(
        default_factory=colls.Map[str, colls.Array[str]]
    )

    def get(self, key: str) -> Maybe[str]:
        return (
            self.map.get(key)
            .filter(lambda v: len(v) == 1)
            .unwrap_or_else(colls.Array[str])
            .first()
        )

    def get_all(self, key: str) -> colls.Array[str]:
        return self.map.get(key).unwrap_or_else(colls.Array[str])

    def items(self) -> Iterable[tuple[str, str]]:
        return ((k, v) for k, vs in self.map.items() for v in vs)

    def keys(self) -> Iterable[str]:
        return self.map.keys()

    def values(self) -> Iterable[str]:
        return (v for vs in self.map.values() for v in vs)

    def __contains__(self, key: str) -> bool:
        return key in self.map

    def __iter__(self) -> Iterator[str]:
        return iter(self.map)


@dataclass(frozen=True, slots=True)
class Headers:
    map: colls.Map[strs.Lowercase, colls.Array[str]] = field(
        default_factory=colls.Map[strs.Lowercase, colls.Array[str]]
    )

    def get(self, key: str) -> Maybe[str]:
        return self.get_all(key).first()

    def get_all(self, key: str) -> colls.Array[str]:
        return self.map.get(strs.Lowercase(key)).unwrap_or_else(colls.Array[str])

    def items(self) -> Iterable[tuple[str, str]]:
        return ((k.value, v) for k, vs in self.map.items() for v in vs)

    def keys(self) -> Iterable[str]:
        return (k.value for k in self.map)

    def values(self) -> Iterable[str]:
        return (v for vs in self.map.values() for v in vs)

    def __contains__(self, key: str) -> bool:
        return strs.Lowercase(key) in self.map

    def __iter__(self) -> Iterator[str]:
        return (k.value for k in self.map)


@dataclass(slots=True)
class MutHeaders:
    map: colls.MutMap[strs.Lowercase, colls.MutArray[str]] = field(
        default_factory=colls.MutMap[strs.Lowercase, colls.MutArray[str]]
    )

    def append(self, key: str, value: str) -> None:
        self.map.set_default(strs.Lowercase(key), colls.MutArray()).append(value)

    def get(self, key: str) -> Maybe[str]:
        return self.get_all(key).first()

    def get_all(self, key: str) -> colls.MutArray[str]:
        return self.map.get(strs.Lowercase(key)).unwrap_or_else(colls.MutArray[str])

    def items(self) -> Iterable[tuple[str, str]]:
        return ((k.value, v) for k, vs in self.map.items() for v in vs)

    def keys(self) -> Iterable[str]:
        return (k.value for k in self.map)

    def pop(self, key: str) -> Result[colls.MutArray[str], errs.KeyErr[str]]:
        return self.map.pop(strs.Lowercase(key)).map_err(
            lambda v: errs.KeyErr(v.key.value)
        )

    def set(self, key: str, value: str) -> None:
        self.map.set(strs.Lowercase(key), colls.MutArray([value]))

    def values(self) -> Iterable[str]:
        return (v for vs in self.map.values() for v in vs)

    def __contains__(self, key: str) -> bool:
        return strs.Lowercase(key) in self.map

    def __iter__(self) -> Iterator[str]:
        return (k.value for k in self.map)


@dataclass(frozen=True, slots=True)
class Queries:
    map: colls.Map[str, colls.Array[str]] = field(
        default_factory=colls.Map[str, colls.Array[str]]
    )

    def get(self, key: str) -> Maybe[str]:
        return self.get_all(key).last()

    def get_all(self, key: str) -> colls.Array[str]:
        return self.map.get(key).unwrap_or_else(colls.Array[str])

    def items(self) -> Iterable[tuple[str, str]]:
        return ((k, v) for k, vs in self.map.items() for v in vs)

    def keys(self) -> Iterable[str]:
        return self.map.keys()

    def values(self) -> Iterable[str]:
        return (v for vs in self.map.values() for v in vs)

    def __contains__(self, key: str) -> bool:
        return key in self.map

    def __iter__(self) -> Iterator[str]:
        return iter(self.map)
