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


def test_create_expense_trims_text_and_rejects_unexpected_fields() -> None:
    """The public API should normalize useful text and reject unknown input."""
    valid_response = client.post(
        "/expenses",
        json={
            "title": "  Groceries  ",
            "amount": 450.75,
            "category": "  Food ",
            "date": "2026-07-31",
        },
    )
    invalid_response = client.post(
        "/expenses",
        json={
            "title": "Lunch",
            "amount": 120.50,
            "category": "Food",
            "date": "2026-07-31",
            "unexpected": "value",
        },
    )

    assert valid_response.status_code == 201
    assert valid_response.json()["title"] == "Groceries"
    assert valid_response.json()["category"] == "Food"
    assert invalid_response.status_code == 422
    assert client.get("/expenses").json() == [valid_response.json()]


@pytest.mark.parametrize(
    "payload",
    [
        {
            "title": "Lunch",
            "amount": 0,
            "category": "Food",
            "date": "2026-07-31",
        },
        {
            "title": "Lunch",
            "amount": 12.345,
            "category": "Food",
            "date": "2026-07-31",
        },
        {
            "title": "   ",
            "amount": 120.50,
            "category": "Food",
            "date": "2026-07-31",
        },
        {
            "title": "Lunch",
            "amount": 120.50,
            "category": "   ",
            "date": "2026-07-31",
        },
        {
            "title": "Lunch",
            "amount": 120.50,
            "category": "Food",
            "date": "31-07-2026",
        },
    ],
)
def test_create_expense_rejects_invalid_payloads(payload: dict[str, object]) -> None:
    """Invalid public input must return 422 and must not create a resource."""
    response = client.post("/expenses", json=payload)

    assert response.status_code == 422
    assert client.get("/expenses").json() == []


def test_list_expenses_is_empty_before_any_expense_is_created() -> None:
    """A new tracker should expose an empty collection, not an error."""
    response = client.get("/expenses")

    assert response.status_code == 200
    assert response.json() == []


def test_list_expenses_returns_every_created_expense_in_creation_order() -> None:
    """A collection read should include every resource in a predictable order."""
    first_expense = create_expense(title="Groceries", amount=450.75, category="Food")
    second_expense = create_expense(title="Metro", amount=40, category="Transport")

    response = client.get("/expenses")

    assert response.status_code == 200
    assert response.json() == [first_expense, second_expense]


def test_list_expenses_can_filter_by_category() -> None:
    """The optional category query parameter should narrow the collection."""
    food_expense = create_expense()
    create_expense(title="Metro", amount=40, category="Transport")

    response = client.get("/expenses", params={"category": "food"})

    assert response.status_code == 200
    assert response.json() == [food_expense]


def test_filter_accepts_surrounding_whitespace_and_unknown_category_returns_empty() -> None:
    """Filtering should be forgiving for users and clear for absent categories."""
    food_expense = create_expense()

    whitespace_response = client.get("/expenses", params={"category": " Food "})
    unknown_response = client.get("/expenses", params={"category": "Travel"})

    assert whitespace_response.status_code == 200
    assert whitespace_response.json() == [food_expense]
    assert unknown_response.status_code == 200
    assert unknown_response.json() == []


def test_empty_category_filter_is_rejected() -> None:
    """An explicitly empty query value is invalid rather than ambiguous."""
    response = client.get("/expenses", params={"category": ""})

    assert response.status_code == 422


def test_list_categories_returns_dropdown_options_from_stored_expenses() -> None:
    """The categories route should expose unique values for a client UI."""
    create_expense(title="Metro", amount=40, category="Transport")
    create_expense(title="Lunch", amount=120.50, category="Food")
    create_expense(title="Groceries", amount=450.75, category="Food")

    response = client.get("/expenses/categories")

    assert response.status_code == 200
    assert response.json() == {"categories": ["Food", "Transport"]}


def test_list_categories_is_empty_when_no_expenses_exist() -> None:
    """A client can safely populate a dropdown before anything is created."""
    response = client.get("/expenses/categories")

    assert response.status_code == 200
    assert response.json() == {"categories": []}


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


def test_summary_of_an_empty_tracker_is_zero() -> None:
    """The summary endpoint should have a useful empty-state response."""
    response = client.get("/expenses/summary")

    assert response.status_code == 200
    assert response.json() == {"total": 0, "by_category": {}}


def test_summary_rounds_common_decimal_addition_to_two_places() -> None:
    """API totals should not expose floating-point representation artifacts."""
    create_expense(title="Tea", amount=0.10, category="Food")
    create_expense(title="Coffee", amount=0.20, category="Food")

    response = client.get("/expenses/summary")

    assert response.status_code == 200
    assert response.json() == {"total": 0.30, "by_category": {"Food": 0.30}}


def test_delete_expense_returns_no_content_and_removes_it() -> None:
    """A successful deletion should return 204 and affect later reads."""
    expense = create_expense()

    delete_response = client.delete(f"/expenses/{expense['id']}")

    assert delete_response.status_code == 204
    assert delete_response.content == b""
    assert client.get("/expenses").json() == []


def test_delete_does_not_reuse_a_previously_assigned_id() -> None:
    """A newly created resource receives a fresh server-assigned identifier."""
    first_expense = create_expense()
    assert client.delete(f"/expenses/{first_expense['id']}").status_code == 204

    new_expense = create_expense(title="Metro", amount=40, category="Transport")

    assert new_expense["id"] == 2


def test_delete_missing_expense_returns_404() -> None:
    """Deleting an absent ID should explain that the resource does not exist."""
    response = client.delete("/expenses/999")

    assert response.status_code == 404
    assert "detail" in response.json()


def test_delete_rejects_a_non_integer_id() -> None:
    """Path-parameter validation should prevent malformed delete requests."""
    response = client.delete("/expenses/not-an-id")

    assert response.status_code == 422


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
