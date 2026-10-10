from remus import Nothing, Some


def test_and_() -> None:
    x = Some(2)
    y = Nothing
    assert x.and_(y) == Nothing

    x = Nothing
    y = Some("foo")
    assert x.and_(y) == Nothing

    x = Some(2)
    y = Some("foo")
    assert x.and_(y) == Some("foo")

    x = Nothing
    y = Nothing
    assert x.and_(y) == Nothing
