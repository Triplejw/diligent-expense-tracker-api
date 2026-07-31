"""End-to-end tests for the public expense API routes."""

import pytest
from fastapi.testclient import TestClient

from expense_tracker.main import app, expense_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_expense_store() -> None:
    """Ensure every test starts with an empty in-memory store."""
    expense_store.clear()


def create_expense(
    title: str = "Groceries",
    amount: float = 450.75,
    category: str = "Food",
    date: str = "2026-07-31",
) -> dict[str, object]:
    """Create one expense through the same endpoint an API client uses."""
    response = client.post(
        "/expenses",
        json={
            "title": title,
            "amount": amount,
            "category": category,
            "date": date,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_create_expense_assigns_an_id_and_returns_the_data() -> None:
    """Creation should return a new resource with HTTP 201."""
    expense = create_expense()

    assert expense == {
        "id": 1,
        "title": "Groceries",
        "amount": 450.75,
        "category": "Food",
        "date": "2026-07-31",
    }


def test_list_expenses_can_filter_by_category() -> None:
    """The optional category query parameter should narrow the collection."""
    food_expense = create_expense()
    create_expense(title="Metro", amount=40, category="Transport")

    response = client.get("/expenses", params={"category": "food"})

    assert response.status_code == 200
    assert response.json() == [food_expense]


def test_list_categories_returns_dropdown_options_from_stored_expenses() -> None:
    """The categories route should expose unique values for a client UI."""
    create_expense(title="Metro", amount=40, category="Transport")
    create_expense(title="Lunch", amount=120.50, category="Food")
    create_expense(title="Groceries", amount=450.75, category="Food")

    response = client.get("/expenses/categories")

    assert response.status_code == 200
    assert response.json() == {"categories": ["Food", "Transport"]}


def test_summary_returns_overall_and_category_totals() -> None:
    """The summary endpoint should calculate both required types of total."""
    create_expense(title="Lunch", amount=120.50, category="Food")
    create_expense(title="Metro", amount=40, category="Transport")

    response = client.get("/expenses/summary")

    assert response.status_code == 200
    assert response.json() == {
        "total": 160.50,
        "by_category": {"Food": 120.50, "Transport": 40.0},
    }


def test_delete_expense_returns_no_content_and_removes_it() -> None:
    """A successful deletion should return 204 and affect later reads."""
    expense = create_expense()

    delete_response = client.delete(f"/expenses/{expense['id']}")

    assert delete_response.status_code == 204
    assert delete_response.content == b""
    assert client.get("/expenses").json() == []


def test_delete_missing_expense_returns_404() -> None:
    """Deleting an absent ID should explain that the resource does not exist."""
    response = client.delete("/expenses/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Expense with id 999 was not found."}


def test_invalid_expense_is_rejected_before_it_reaches_storage() -> None:
    """FastAPI and Pydantic should reject invalid request data with HTTP 422."""
    response = client.post(
        "/expenses",
        json={
            "title": "",
            "amount": 0,
            "category": "Food",
            "date": "not-a-date",
        },
    )

    assert response.status_code == 422
    assert client.get("/expenses").json() == []
