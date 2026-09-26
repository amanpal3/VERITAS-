"""
VERITAS Backend - Health Check Test Suite
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_check_api_v1(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "veritas-api"
    assert data["graph_backend"] in ["in_memory_networkx", "neo4j"]
    assert data["total_nodes"] >= 29
    assert data["total_edges"] >= 33


def test_health_check_root_alias(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_index(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"
