"""Tests for the in-memory expense store."""

from expense_tracker.models import ExpenseCreate
from expense_tracker.storage import ExpenseStore


def make_expense(title: str, amount: float, category: str) -> ExpenseCreate:
    """Create valid test data with a fixed date."""
    return ExpenseCreate(
        title=title,
        amount=amount,
        category=category,
        date="2026-07-31",
    )


def test_store_assigns_ids_and_filters_categories() -> None:
    """Expenses should receive sequential IDs and support case-insensitive filters."""
    store = ExpenseStore()
    groceries = store.create(make_expense("Groceries", 450.75, "Food"))
    taxi = store.create(make_expense("Taxi", 250, "Transport"))

    assert groceries.id == 1
    assert taxi.id == 2
    assert store.list_expenses(category=" food ") == [groceries]


def test_store_summary_and_delete() -> None:
    """Totals should group expenses, and deletion should report its outcome."""
    store = ExpenseStore()
    first_food_expense = store.create(make_expense("Lunch", 120.50, "Food"))
    store.create(make_expense("Groceries", 450.75, "Food"))
    store.create(make_expense("Metro", 40, "Transport"))

    total, totals_by_category = store.summary()

    assert total == 611.25
    assert totals_by_category == {"Food": 571.25, "Transport": 40.0}
    assert store.delete(first_food_expense.id) is True
    assert store.delete(first_food_expense.id) is False


def test_store_lists_distinct_categories_alphabetically() -> None:
    """A client should receive one predictable option for each category."""
    store = ExpenseStore()
    store.create(make_expense("Metro", 40, "Transport"))
    store.create(make_expense("Lunch", 120.50, "Food"))
    store.create(make_expense("Groceries", 450.75, "Food"))

    assert store.list_categories() == ["Food", "Transport"]
