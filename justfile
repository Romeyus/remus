check:
    @uv run basedpyright
    @uv run ruff check

coverage:
    @just test --cov=src/remus --cov-report=term-missing

test *options:
    @uv run pytest {{ options }}
