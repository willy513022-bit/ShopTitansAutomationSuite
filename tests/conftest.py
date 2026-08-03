from __future__ import annotations

import pytest

from tests.mock_input_driver import MockInputDriver


@pytest.fixture
def mock_driver() -> MockInputDriver:
    """
    提供測試用的 MockInputDriver。
    """
    return MockInputDriver()