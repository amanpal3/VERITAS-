"""
VERITAS Backend - Centrality and Communities Test Suite
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_centrality_betweenness(client: TestClient):
    response = client.get("/api/v1/analytics/centrality?metric=betweenness&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["metric"] == "betweenness"
    assert len(data["rankings"]) > 0
    scores = [item["score"] for item in data["rankings"]]
    assert scores == sorted(scores, reverse=True)


def test_centrality_pagerank(client: TestClient):
    response = client.get("/api/v1/analytics/centrality?metric=pagerank&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["metric"] == "pagerank"
    assert len(data["rankings"]) > 0


def test_centrality_degree(client: TestClient):
    response = client.get("/api/v1/analytics/centrality?metric=degree&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["metric"] == "degree"
    assert len(data["rankings"]) > 0


def test_centrality_invalid_metric(client: TestClient):
    response = client.get("/api/v1/analytics/centrality?metric=magic_score")
    assert response.status_code == 400
    error = response.json().get("error", {})
    assert error.get("code") == "INVALID_METRIC"


def test_communities_detection(client: TestClient):
    response = client.get("/api/v1/communities")
    assert response.status_code == 200
    data = response.json()
    assert data["total_communities"] >= 3
    assert len(data["communities"]) >= 3
    labels = [c["label"] for c in data["communities"]]
    assert any("Logistics" in l or "Smuggling" in l for l in labels)
    assert any("Financial" in l or "Hawala" in l for l in labels)


def test_communities_alias(client: TestClient):
    response = client.get("/api/v1/analytics/communities")
    assert response.status_code == 200
    data = response.json()
    assert data["total_communities"] >= 3
