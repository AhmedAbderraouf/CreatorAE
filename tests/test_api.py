"""
Basic smoke tests for the CreatorAE FastAPI endpoints.
Run with: pytest tests/
"""

from fastapi.testclient import TestClient

# Lazy import so tests don't require a live OpenAI key just to check routing
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from unittest.mock import patch


def get_test_client():
    from app.api.main import app
    return TestClient(app)


def test_health_check():
    client = get_test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "CreatorAE API running"}


def test_query_missing_body():
    client = get_test_client()
    response = client.post("/query", json={})
    assert response.status_code == 422  # Pydantic validation error


def test_query_too_short():
    client = get_test_client()
    response = client.post("/query", json={"question": "hi"})
    assert response.status_code == 422


@patch("app.api.main.rag_query")
def test_query_success(mock_rag):
    mock_rag.return_value = {
        "answer": "Based on retrieved context, a permit may be required.",
        "sources": ["Advertiser-Guide.pdf"],
    }
    client = get_test_client()
    response = client.post(
        "/query",
        json={"question": "Do I need a permit to film inside a mall?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert isinstance(data["sources"], list)
