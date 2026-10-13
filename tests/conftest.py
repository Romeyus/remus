from unittest import mock

import pytest


@pytest.fixture
def func() -> mock.Mock:
    return mock.Mock()
