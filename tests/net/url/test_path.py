from remus.net import url


def test__new__() -> None:
    assert url.Path("/hello/world") == "/hello/world"
    assert url.Path("hello/world") == "/hello/world"
    assert url.Path("//hello//world") == "/hello/world"
    assert url.Path("hello/world/") == "/hello/world"
    assert url.Path("/hello/world/") == "/hello/world"
