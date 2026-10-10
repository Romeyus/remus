from remus import Maybe, Nothing, Some


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


def test_and_then() -> None:
    def sq_then_to_str(x: int) -> Maybe[str]:
        if x > 1_000_000:
            return Nothing
        return Some(str(x**2))

    assert Some(2).and_then(sq_then_to_str) == Some("4")
    assert Some(1_000_001).and_then(sq_then_to_str) == Nothing  # overflowed
    assert Nothing.and_then(sq_then_to_str) == Nothing
