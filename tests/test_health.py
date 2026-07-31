"""Smoke tests for the application setup."""

from fastapi.testclient import TestClient

from expense_tracker.main import app

client = TestClient(app)


def test_base_url_redirects_to_interactive_docs() -> None:
    """Opening the server URL in a browser should lead to usable API docs."""
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/docs"


def test_health_check_returns_ok() -> None:
    """The API should report that it is available."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
