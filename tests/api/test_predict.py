"""
Integration tests for the FastAPI inference endpoints.

Tests the health check and prediction endpoints to ensure proper
input validation and response formatting.
"""

import pytest


@pytest.mark.asyncio
async def test_health_endpoint(async_client):
    """
    Verify that the /v1/health endpoint returns a 200 OK and correct JSON.
    """
    response = await async_client.get("/v1/health")

    # Assert HTTP status
    assert response.status_code == 200

    # Assert response payload structure
    data = response.json()
    assert data["status"] == "healthy"
    assert "model_loaded" in data


@pytest.mark.asyncio
async def test_predict_requires_model(async_client):
    """
    Verify that the /v1/predict endpoint enforces strict input validation.

    This test omits 'latitude' and 'longitude' which are required fields,
    expecting a 422 Unprocessable Entity response from Pydantic.
    """
    # Arrange: invalid payload (missing lat/lon)
    payload = {
        "station": "IGI Airport",
        "season": "Winter",
        "temperature": 14.5,
        "humidity": 82.0,
        "wind_speed": 3.2,
        "visibility": 2.1,
        "month": 1,
        "hour": 8,
        "day_of_week": "Monday",
    }

    # Act: POST to predict endpoint
    response = await async_client.post("/v1/predict", json=payload)

    # Assert: 422 Unprocessable Entity due to missing required fields
    assert response.status_code == 422
