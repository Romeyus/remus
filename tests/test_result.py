from remus import Err, Ok, Result


def test_and_() -> None:
    x = Ok(2)
    y = Err("late error")
    assert x.and_(y) == Err("late error")

    x = Err("early error")
    y = Ok("foo")
    assert x.and_(y) == Err("early error")

    x = Err("not a 2")
    y = Err("late error")
    assert x.and_(y) == Err("not a 2")

    x = Ok(2)
    y = Ok("different result type")
    assert x.and_(y) == Ok("different result type")


def test_and_then() -> None:
    def sq_then_to_str(x: int) -> Result[str, str]:
        if x > 1_000_000:
            return Err("overflowed")
        return Ok(str(x**2))

    assert Ok(2).and_then(sq_then_to_str) == Ok("4")
    assert Ok(1_000_001).and_then(sq_then_to_str) == Err("overflowed")
    assert Err("not a number").and_then(sq_then_to_str) == Err("not a number")
