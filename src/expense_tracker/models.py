"""Pydantic models that define the Expense Tracker API data contract."""

from datetime import date as Date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExpenseCreate(BaseModel):
    """Fields a client must provide when creating an expense."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(
        min_length=1,
        max_length=120,
        description="A short description of the expense.",
        examples=["Groceries"],
    )
    amount: float = Field(
        gt=0,
        le=1_000_000,
        multiple_of=0.01,
        description="Expense amount, expressed to two decimal places.",
        examples=[450.75],
    )
    category: str = Field(
        min_length=1,
        max_length=50,
        description="The category used to group the expense.",
        examples=["Food"],
    )
    date: Date = Field(
        description="The date the expense was incurred, in YYYY-MM-DD format.",
        examples=["2026-07-31"],
    )

    @field_validator("title", "category")
    @classmethod
    def text_fields_must_contain_visible_characters(cls, value: str) -> str:
        """Trim text fields and reject values made only of whitespace."""
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("must contain at least one non-whitespace character")
        return cleaned_value


class Expense(ExpenseCreate):
    """An expense after the API has assigned its identifier."""

    id: int = Field(gt=0, description="The server-assigned expense identifier.")


class ExpenseSummary(BaseModel):
    """The overall expense total and the total for each category."""

    total: float = Field(description="The total of every stored expense.")
    by_category: dict[str, float] = Field(
        description="Expense totals grouped by category.",
    )


class CategoryList(BaseModel):
    """The distinct expense categories available for client selection."""

    categories: list[str] = Field(
        description="Unique stored categories, sorted alphabetically.",
        examples=[["Food", "Transport"]],
    )


class HealthResponse(BaseModel):
    """A successful health-check response."""

    status: Literal["ok"]
