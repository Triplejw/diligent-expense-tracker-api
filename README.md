# Smart Expense Tracker API

A REST API for managing personal expenses, built for Diligent's Software
Engineering Apprenticeship 2026 take-home assignment.

## Overview

This project is a backend-only REST API. A client sends JSON requests to
FastAPI, Pydantic validates the data, the in-memory store performs the
operation, and the API returns a documented JSON response.

```text
HTTP request -> FastAPI route -> Pydantic validation -> in-memory store -> JSON response
```

The API supports the required expense-management operations:

- Create an expense with a server-assigned ID, title, amount, category, and date.
- List all expenses or filter them by category.
- List the currently used categories so a client can populate a category
  dropdown automatically.
- Calculate the total of all expenses and totals grouped by category.
- Delete an expense by ID.
- Validate input before it reaches storage, including required text, a positive
  two-decimal-place amount, and an ISO 8601 date.

Data is stored in memory, as permitted by the assignment. It is intentionally
cleared whenever the server restarts; no database is required.

FastAPI automatically provides interactive OpenAPI/Swagger documentation at
`/docs`, which is included as the selected optional bonus.

## Requirements

- Python 3.9 or newer

## Install dependencies

From a fresh clone, run these exact commands from the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[dev]"
```

Using `.venv/bin/python` makes the commands work without relying on an
activated shell or a globally installed Python package.

## Run the server

```bash
.venv/bin/python -m uvicorn expense_tracker.main:app --host 127.0.0.1 --port 8000 --reload
```

The server starts at `http://127.0.0.1:8000`.

- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

## Run the tests

```bash
.venv/bin/python -m pytest
```

The command runs API-contract tests, focused unit tests, and a line-coverage
report. It fails if the application code is below 100% line coverage. Coverage
is a useful safety check, not a substitute for testing meaningful behaviour.

## API endpoints

| Method | Path | Description | Success response |
| --- | --- | --- | --- |
| `GET` | `/health` | Confirm the API server is running. | `200 OK` |
| `POST` | `/expenses` | Create an expense. | `201 Created` |
| `GET` | `/expenses` | List every expense. | `200 OK` |
| `GET` | `/expenses?category=Food` | List expenses in one category. Filtering ignores case and surrounding spaces. | `200 OK` |
| `GET` | `/expenses/categories` | List distinct categories for a client-side dropdown. | `200 OK` |
| `GET` | `/expenses/summary` | Return the overall total and totals grouped by category. | `200 OK` |
| `DELETE` | `/expenses/{expense_id}` | Delete an expense by its ID. | `204 No Content` |

### Create an expense

Send this JSON body to `POST /expenses`:

```json
{
  "title": "Groceries",
  "amount": 450.75,
  "category": "Food",
  "date": "2026-07-31"
}
```

The server responds with the stored expense and assigns its `id`:

```json
{
  "id": 1,
  "title": "Groceries",
  "amount": 450.75,
  "category": "Food",
  "date": "2026-07-31"
}
```

### Category options for a client dropdown

`GET /expenses/categories` returns categories created through `POST /expenses`:

```json
{
  "categories": ["Food", "Transport"]
}
```

Swagger documents and tests this endpoint, but a dynamic dropdown itself is a
frontend feature. A web or mobile client would call this endpoint and render
the returned values as its dropdown options.

### Expense summary response

`GET /expenses/summary` returns both required totals in one request:

```json
{
  "total": 900.75,
  "by_category": {
    "Food": 450.75,
    "Transport": 450.0
  }
}
```

## End-to-end API demonstration

First start the server with the command in **Run the server**. Open a second
terminal in the repository root, then run the following commands. They exercise
every required operation against the running API.

```bash
curl -sS -X POST http://127.0.0.1:8000/expenses \
  -H "Content-Type: application/json" \
  -d '{"title":"Groceries","amount":450.75,"category":"Food","date":"2026-07-31"}'

curl -sS -X POST http://127.0.0.1:8000/expenses \
  -H "Content-Type: application/json" \
  -d '{"title":"Metro","amount":40.00,"category":"Transport","date":"2026-07-31"}'

curl -sS http://127.0.0.1:8000/expenses
curl -sS "http://127.0.0.1:8000/expenses?category=Food"
curl -sS http://127.0.0.1:8000/expenses/categories
curl -sS http://127.0.0.1:8000/expenses/summary
curl -i -X DELETE http://127.0.0.1:8000/expenses/1
```

The final command returns `204 No Content`. A later `GET /expenses` will show
only the remaining expense.

## Clean-checkout verification

To verify a submission from a clean checkout, clone the repository into a new
directory and follow these sections in order:

1. **Install dependencies**
2. **Run the tests** — the suite should pass and report 100% line coverage
3. **Run the server**
4. **End-to-end API demonstration** or test the same routes through Swagger

## Project structure

```text
.
├── README.md                 # Setup, run, test, and API instructions
├── AI_NOTES.md               # Record of AI-assisted development
├── src/
│   └── expense_tracker/
│       ├── main.py           # FastAPI application and HTTP routes
│       ├── models.py         # Request and response validation models
│       └── storage.py        # In-memory expense storage and calculations
└── tests/                    # Validation, storage, and API route tests
```
