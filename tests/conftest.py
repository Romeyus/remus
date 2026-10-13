from unittest import mock

import pytest


@pytest.fixture
def factory() -> mock.Mock:
    return mock.Mock()


@pytest.fixture
def func() -> mock.Mock:
    return mock.Mock()
