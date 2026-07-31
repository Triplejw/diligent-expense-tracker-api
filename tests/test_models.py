"""Tests for request validation rules."""

from datetime import date

import pytest
from pydantic import ValidationError

from expense_tracker.models import ExpenseCreate


def test_expense_create_trims_text_fields() -> None:
    """Useful text should be retained without accidental outer whitespace."""
    expense = ExpenseCreate(
        title="  Groceries  ",
        amount=450.75,
        category="  Food ",
        date="2026-07-31",
    )

    assert expense.title == "Groceries"
    assert expense.category == "Food"
    assert expense.date == date(2026, 7, 31)


@pytest.mark.parametrize("amount", [0, -1, 12.345])
def test_expense_create_rejects_invalid_amounts(amount: float) -> None:
    """Amounts must be positive and have no more than two decimal places."""
    with pytest.raises(ValidationError):
        ExpenseCreate(
            title="Lunch",
            amount=amount,
            category="Food",
            date="2026-07-31",
        )


def test_expense_create_rejects_whitespace_only_title() -> None:
    """A required text field cannot contain only spaces."""
    with pytest.raises(ValidationError):
        ExpenseCreate(
            title="   ",
            amount=100,
            category="Food",
            date="2026-07-31",
        )
