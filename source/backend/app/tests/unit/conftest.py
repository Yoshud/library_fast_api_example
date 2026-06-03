from contextlib import asynccontextmanager
from unittest.mock import AsyncMock

import pytest


@asynccontextmanager
async def noop_transaction(db):
    """No-op replacement for optional_transaction in unit tests."""
    yield


@pytest.fixture
def mock_db():
    """Provide a mock AsyncSession for unit tests."""
    return AsyncMock()
