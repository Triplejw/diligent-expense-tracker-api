"""HTTP routes for the Expense Tracker API."""

from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.responses import RedirectResponse

from .models import (
    CategoryList,
    Expense,
    ExpenseCreate,
    ExpenseSummary,
    HealthResponse,
)
from .storage import ExpenseStore

app = FastAPI(
    title="Smart Expense Tracker API",
    version="0.1.0",
    description="A REST API for managing personal expenses.",
)
expense_store = ExpenseStore()


@app.get("/", include_in_schema=False)
def redirect_to_api_docs() -> RedirectResponse:
    """Send a browser visiting the base URL to the interactive API docs."""
    return RedirectResponse(url="/docs")


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health_check() -> HealthResponse:
    """Report whether the API server is running."""
    return HealthResponse(status="ok")


@app.post(
    "/expenses",
    response_model=Expense,
    status_code=status.HTTP_201_CREATED,
    tags=["expenses"],
)
def create_expense(expense_data: ExpenseCreate) -> Expense:
    """Add a validated expense and return it with a server-assigned ID."""
    return expense_store.create(expense_data)


@app.get("/expenses", response_model=list[Expense], tags=["expenses"])
def list_expenses(
    category: Optional[str] = Query(
        default=None,
        min_length=1,
        max_length=50,
        description="Optionally return only expenses in this category.",
        examples=["Food"],
    ),
) -> list[Expense]:
    """Return every expense, optionally filtered by category."""
    return expense_store.list_expenses(category=category)


@app.get(
    "/expenses/categories",
    response_model=CategoryList,
    tags=["expenses"],
)
def list_categories() -> CategoryList:
    """Return the categories currently available for a client-side dropdown."""
    return CategoryList(categories=expense_store.list_categories())


@app.get("/expenses/summary", response_model=ExpenseSummary, tags=["expenses"])
def get_expense_summary() -> ExpenseSummary:
    """Calculate the overall total and the total for every category."""
    total, totals_by_category = expense_store.summary()
    return ExpenseSummary(total=total, by_category=totals_by_category)


@app.delete(
    "/expenses/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["expenses"],
)
def delete_expense(expense_id: int) -> Response:
    """Delete an expense by ID or return a clear not-found error."""
    if not expense_store.delete(expense_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with id {expense_id} was not found.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
