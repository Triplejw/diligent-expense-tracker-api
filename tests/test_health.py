"""Smoke tests for the application setup."""

from fastapi.testclient import TestClient

from expense_tracker.main import app

client = TestClient(app)


def test_health_check_returns_ok() -> None:
    """The API should report that it is available."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
