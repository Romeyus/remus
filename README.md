# remus

The functional programming toolkit for Python.

## Installation

Using uv (recommended):

```bash
uv add remus
```

Using pip:

```bash
pip install remus
```

## Example

Using the `Result` monad:

```python
from remus import Err, Ok, Result

def divide(x: float, y: float) -> Result[float, str]:
    if y == 0:
        return Err("cannot divide by zero")

    return Ok(x / y)


def sq_then_to_str(x: int) -> str:
    return str(x**2)


def main() -> None:
    result = divide(10, 2).map(int).map(sq_then_to_str)
    print(result) # >> Ok(value="25")
    print(result.unwrap()) # >> "25"

    result = divide(100, 0).map(int).map(sq_then_to_str)
    print(result) # >> Err(value="cannot divide by zero")
    print(result.unwrap_or("0")) # >> "0"
```

Using the `Maybe` monad:

```python
from remus import Maybe, Nothing, Some


users = {
    1: "Ada",
    2: "Grace",
}


def find_user(user_id: int) -> Maybe[str]:
    user = users.get(user_id)

    if user is None:
        return Nothing

    return Some(user)


def uppercase(name: str) -> str:
    return name.upper()


def main() -> None:
    result = find_user(1).map(uppercase)
    print(result)  # >> Some(value="ADA")
    print(result.unwrap())  # >> "ADA"

    result = find_user(3).map(uppercase)
    print(result)  # >> NothingType(value=None)
    print(result.unwrap_or("Unknown user"))  # >> "Unknown user"

```
