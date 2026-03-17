"""
Pytest configuration and shared fixtures for AirSense ML.

Provides shared resources like the async HTTP client for FastAPI integration tests.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from api.app import app


class MockPredictor:
    """Mock predictor to avoid loading heavy models during tests."""

    model_version = "mock-1.0"


@pytest.fixture
async def async_client():
    """
    Provide an asynchronous test client for the FastAPI application.

    Uses ASGITransport to bypass the actual network layer, making tests
    fast and reliable while fully exercising the FastAPI stack.
    Bypasses the application lifespan by mocking the predictor.

    Yields:
        httpx.AsyncClient connected to the FastAPI app.
    """
    # Mock the predictor to bypass loading the actual pickle file
    app.state.predictor = MockPredictor()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
