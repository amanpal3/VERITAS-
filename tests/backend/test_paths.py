"""
VERITAS Backend - Path Finder Endpoints Test Suite
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_shortest_path_found(client: TestClient):
    response = client.get("/api/v1/paths/shortest?source=P006&target=P001")
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "P006"
    assert data["target"] == "P001"
    assert data["found"] is True
    assert data["length"] >= 1
    assert len(data["nodes"]) >= 2
    assert data["nodes"][0] == "P006"
    assert data["nodes"][-1] == "P001"
    assert len(data["edges"]) == len(data["nodes"]) - 1
    assert len(data["path_details"]) == len(data["edges"])

    first_step = data["path_details"][0]
    assert "step" in first_step
    assert "from" in first_step
    assert "to" in first_step
    assert "relation" in first_step


def test_shortest_path_alias(client: TestClient):
    response = client.get("/api/v1/path?source=P006&target=P001")
    assert response.status_code == 200
    data = response.json()
    assert data["found"] is True


def test_shortest_path_nonexistent_node(client: TestClient):
    response = client.get("/api/v1/paths/shortest?source=P9999&target=P001")
    assert response.status_code == 404
    error = response.json().get("error", {})
    assert error.get("code") == "ENTITY_NOT_FOUND"
