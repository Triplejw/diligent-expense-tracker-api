"""In-memory storage for expenses.

The assignment permits in-memory data, so this class intentionally keeps the
implementation small and avoids database setup. Data is cleared on restart.
"""

from collections import defaultdict
from typing import Optional

from .models import Expense, ExpenseCreate


class ExpenseStore:
    """Manage expenses and their server-assigned integer identifiers."""

    def __init__(self) -> None:
        self._expenses: dict[int, Expense] = {}
        self._next_id = 1

    def create(self, expense_data: ExpenseCreate) -> Expense:
        """Store and return a newly created expense."""
        expense = Expense(id=self._next_id, **expense_data.model_dump())
        self._expenses[expense.id] = expense
        self._next_id += 1
        return expense

    def list_expenses(self, category: Optional[str] = None) -> list[Expense]:
        """Return all expenses, optionally filtered by category.

        Category matching ignores case and surrounding whitespace so that a
        query for ``food`` also finds an expense saved as ``Food``.
        """
        expenses = list(self._expenses.values())
        if category is None:
            return expenses

        normalized_category = category.strip().casefold()
        return [
            expense
            for expense in expenses
            if expense.category.casefold() == normalized_category
        ]

    def delete(self, expense_id: int) -> bool:
        """Delete an expense and report whether it existed."""
        return self._expenses.pop(expense_id, None) is not None

    def list_categories(self) -> list[str]:
        """Return distinct stored categories in a predictable order."""
        categories = {expense.category for expense in self._expenses.values()}
        return sorted(categories, key=str.casefold)

    def summary(self) -> tuple[float, dict[str, float]]:
        """Calculate an overall total and totals grouped by category."""
        totals_by_category: defaultdict[str, float] = defaultdict(float)
        for expense in self._expenses.values():
            totals_by_category[expense.category] += expense.amount

        rounded_category_totals = {
            category: round(total, 2)
            for category, total in sorted(totals_by_category.items())
        }
        overall_total = round(sum(rounded_category_totals.values()), 2)
        return overall_total, rounded_category_totals

    def clear(self) -> None:
        """Reset storage; useful for isolating automated tests."""
        self._expenses.clear()
        self._next_id = 1
