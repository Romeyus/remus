import pytest

from remus import Err, Ok


class TestOk:
    @pytest.fixture
    def ok(self) -> Ok[int]:
        return Ok(1)


class TestErr:
    @pytest.fixture
    def err(self) -> Err[str]:
        return Err("An error occurred.")
