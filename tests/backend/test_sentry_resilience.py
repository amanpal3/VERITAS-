"""
VERITAS Backend - Sentry Error Tracking and Resilience Tests
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.core.exceptions import VeritasAPIException
from backend.app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_standard_error_shape_consistency(client: TestClient):
    response = client.get("/api/v1/entities/NON_EXISTENT_ID")
    assert response.status_code == 404
    body = response.json()
    assert "error" in body
    assert "code" in body["error"]
    assert "message" in body["error"]
    assert body["error"]["code"] == "ENTITY_NOT_FOUND"


def test_sentry_exception_capture_in_route():
    from backend.app.core.exceptions import unhandled_exception_handler
    from unittest.mock import MagicMock, patch

    mock_request = MagicMock()
    mock_request.method = "GET"
    mock_request.url.path = "/api/v1/test-error"

    test_exception = RuntimeError("Simulated critical failure")

    with patch("sentry_sdk.capture_exception") as mock_sentry:
        import asyncio
        response = asyncio.run(unhandled_exception_handler(mock_request, test_exception))
        assert response.status_code == 500
        mock_sentry.assert_called_once_with(test_exception)
