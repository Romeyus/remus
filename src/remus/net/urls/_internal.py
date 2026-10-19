from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from http import HTTPMethod
from typing import Self

from remus import Err, Maybe, Ok, Result, colls, errs, panic, strs

try:
    import nanoroute

except ImportError:  # pragma: no cover
    panic("missing dependency, install 'remus[net]'")

# ==========================================
# ===            Types                 ===
# ==========================================
type PathParams = colls.Map[str, str]
type RouteErr = NotFoundErr | MethodNotAllowedErr


# ==========================================
# ===            Routing                 ===
# ==========================================
class Path(str):
    def __new__(cls, value: str) -> Self:
        parts = [p for p in value.split("/") if p]
        normalised = "/".join(parts)
        return super().__new__(cls, f"/{normalised}")


@dataclass(frozen=True, slots=True)
class RouteMatch[T]:
    target: T
    params: PathParams


class Router[T]:
    def __init__(self) -> None:
        self._nanorouter = nanoroute.router()  # type: ignore

    def map(
        self, path: Path, methods: HTTPMethod | Iterable[HTTPMethod], target: T
    ) -> None:
        if isinstance(methods, HTTPMethod):
            all_methods = {methods}
        else:
            all_methods = set(methods)

        if HTTPMethod.GET in all_methods:
            all_methods.add(HTTPMethod.HEAD)

        self._nanorouter.route(all_methods, path)(target)

    def match(self, path: Path, method: HTTPMethod) -> Result[RouteMatch[T], RouteErr]:
        try:
            target, params = self._nanorouter.lookup(method, path)
            return Ok(RouteMatch(target, colls.Map(params)))

        except LookupError:
            allowed_methods: list[HTTPMethod] = []

            for m in HTTPMethod:
                try:
                    self._nanorouter.lookup(m, path)
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
class Cookies:
    def __init__(self, data: Mapping[str, Iterable[str]] | None = None) -> None:
        if data is None:
            self._map: colls.Map[str, colls.Array[str]] = colls.Map()
            return

        self._map = colls.Map({k: colls.Array(v) for k, v in data.items()})

    def get(self, key: str) -> Maybe[str]:
        return (
            self._map.get(key)
            .filter(lambda v: len(v) == 1)
            .unwrap_or_else(colls.Array[str])
            .first()
        )

    def get_all(self, key: str) -> colls.Array[str]:
        return self._map.get(key).unwrap_or_else(colls.Array[str])

    def items(self) -> Iterable[tuple[str, str]]:
        return ((k, v) for k, vs in self._map.items() for v in vs)

    def keys(self) -> Iterable[str]:
        return self._map.keys()

    def values(self) -> Iterable[str]:
        return (v for vs in self._map.values() for v in vs)

    def __contains__(self, key: str) -> bool:
        return key in self._map

    def __iter__(self) -> Iterator[str]:
        return iter(self._map)


class Headers:
    def __init__(self, data: Mapping[str, Iterable[str]] | None = None) -> None:
        if data is None:
            self._map: colls.Map[strs.Lowercase, colls.Array[str]] = colls.Map()
            return

        self._map = colls.Map(
            {strs.Lowercase(k): colls.Array(v) for k, v in data.items()}
        )

    def get(self, key: str) -> Maybe[str]:
        return self.get_all(key).first()

    def get_all(self, key: str) -> colls.Array[str]:
        return self._map.get(strs.Lowercase(key)).unwrap_or_else(colls.Array[str])

    def items(self) -> Iterable[tuple[str, str]]:
        return ((k, v) for k, vs in self._map.items() for v in vs)

    def keys(self) -> Iterable[str]:
        return self._map.keys()

    def values(self) -> Iterable[str]:
        return (v for vs in self._map.values() for v in vs)

    def __contains__(self, key: str) -> bool:
        return strs.Lowercase(key) in self._map

    def __iter__(self) -> Iterator[str]:
        return iter(self._map)


class MutHeaders:
    def __init__(self, data: Mapping[str, Iterable[str]] | None = None) -> None:
        if data is None:
            self._map: colls.MutMap[strs.Lowercase, colls.MutArray[str]] = (
                colls.MutMap()
            )
            return

        self._map = colls.MutMap(
            {strs.Lowercase(k): colls.MutArray(v) for k, v in data.items()}
        )

    def append(self, key: str, value: str) -> None:
        self._map.set_default(strs.Lowercase(key), colls.MutArray()).append(value)

    def get(self, key: str) -> Maybe[str]:
        return self.get_all(key).first()

    def get_all(self, key: str) -> colls.MutArray[str]:
        return self._map.get(strs.Lowercase(key)).unwrap_or_else(colls.MutArray[str])

    def items(self) -> Iterable[tuple[str, str]]:
        return ((k, v) for k, vs in self._map.items() for v in vs)

    def keys(self) -> Iterable[str]:
        return self._map.keys()

    def pop(self, key: str) -> Result[colls.MutArray[str], errs.KeyErr[str]]:
        return self._map.pop(strs.Lowercase(key)).map_err(lambda v: errs.KeyErr(v.key))

    def set(self, key: str, value: str) -> None:
        self._map.set(strs.Lowercase(key), colls.MutArray([value]))

    def values(self) -> Iterable[str]:
        return (v for vs in self._map.values() for v in vs)

    def __contains__(self, key: str) -> bool:
        return strs.Lowercase(key) in self._map

    def __iter__(self) -> Iterator[str]:
        return iter(self._map)


class Queries:
    def __init__(self, data: Mapping[str, Iterable[str]] | None = None) -> None:
        if data is None:
            self._map: colls.Map[str, colls.Array[str]] = colls.Map()
            return

        self._map = colls.Map({k: colls.Array(v) for k, v in data.items()})

    def get(self, key: str) -> Maybe[str]:
        return self.get_all(key).last()

    def get_all(self, key: str) -> colls.Array[str]:
        return self._map.get(key).unwrap_or_else(colls.Array[str])

    def items(self) -> Iterable[tuple[str, str]]:
        return ((k, v) for k, vs in self._map.items() for v in vs)

    def keys(self) -> Iterable[str]:
        return self._map.keys()

    def values(self) -> Iterable[str]:
        return (v for vs in self._map.values() for v in vs)

    def __contains__(self, key: str) -> bool:
        return key in self._map

    def __iter__(self) -> Iterator[str]:
        return iter(self._map)
