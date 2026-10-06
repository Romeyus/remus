# remus

The functional programming toolkit for Python.

## Installation

Using **uv** (recommended):

```bash
uv add remus
```

Using pip:

```bash
pip install remus
```

## Quickstart

```python
from remus import Err, Ok, Result

def divide(a: float, b: float) -> Result[float, ZeroDivisionError]:
    try:
        return Ok(a / b)

    except ZeroDivisionError as e:
        return Err(e)


def main() -> None:
    result = (
        divide(10, 0)
        .map(lambda v: v**2)
        .unwrap_or(100)
    )
    print(result) # >> 100


if __name__ == "__main__":
    main()
```
