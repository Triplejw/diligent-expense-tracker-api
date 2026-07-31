# AI Usage Notes

## AI tool used

I used ChatGPT Codex as a pair-programming and learning assistant while
building this take-home assignment.

## AI-assisted code and my contribution

Codex drafted the initial implementation for the project scaffold, Pydantic
validation models, in-memory storage class, FastAPI routes, automated tests,
and the initial documentation.

I did not treat that output as a finished solution. I reviewed the API design
and made the final decisions to use Python, FastAPI, Uvicorn, server-assigned
IDs, an in-memory store, and Swagger/OpenAPI as the single optional bonus. I
created the GitHub repository, set up the local Python environment, ran the
application, and interacted with the API myself.

## What I validated, tested, or changed

- I read through the generated project structure and code to understand the
  flow from request validation to storage and the HTTP response.
- I ran the complete automated test suite with `python -m pytest`; it passed
  with 32 tests and 100% line coverage across the application package.
- I started the Uvicorn server locally and used FastAPI's Swagger UI to send
  real requests. I verified creation, listing, category filtering, the summary
  response, and deletion through the running API.
- During final review, I identified that Swagger's free-text category filter
  cannot dynamically become a dropdown from live API data. I chose to add
  `GET /expenses/categories`, which returns unique stored categories so a
  future web or mobile client can populate its own dropdown automatically.
- I requested a final README review focused on the assignment's automated
  evaluation requirement. The README now uses explicit `.venv/bin/python`
  commands for installation, server startup, and tests, and includes an
  end-to-end `curl` demonstration of every required API operation.
- The initial implementation used the newer `str | None` type syntax. It was
  changed to `Optional[str]` because the project supports Python 3.9, where
  that newer syntax is not available.
- I kept the test fixture that clears the in-memory store before each route
  test so tests do not accidentally depend on data created by earlier tests.
- I expanded the test suite around the public HTTP contract: success paths,
  empty states, invalid payloads, query validation, filtering, summaries, and
  deletion. These tests assert observable request/response behaviour instead
  of relying on the store's private dictionary structure.
- I added `pytest-cov` and configured the normal test command to require 100%
  line coverage for the small application package. I treat that as a guard
  against untested lines, not proof that the API has no bugs.
- During final manual verification, I noticed that the base server URL had no
  route even though `/docs` worked. I added a small `GET /` redirect to `/docs`
  and a contract test, so opening the stated server address now leads directly
  to the interactive documentation.

## AI suggestions I chose not to use

- I did not use a local JSON file or a SQL database. The assignment explicitly
  permits in-memory storage, and it keeps the solution focused on API design,
  validation, and tests rather than file or database setup.
- I did not add Docker. The brief says to choose at most one optional bonus;
  Swagger/OpenAPI documentation is already included naturally by FastAPI and
  is more useful for evaluating this API.
- I did not add search or a monthly-summary endpoint. Those are also listed as
  optional bonuses, and the brief says to choose at most one. Keeping
  Swagger/OpenAPI as the single bonus avoids unnecessary scope and follows the
  instruction exactly.
- I did not build a separate frontend only to display a dropdown. The
  assignment asks for an API, so the categories endpoint provides the backend
  capability without expanding the project beyond its intended scope.
- I did not switch to Node.js/TypeScript. It was an allowed alternative, but I
  chose FastAPI because I could build, test, and explain a reliable solution
  within the stated timebox.
- I considered using `Decimal` for currency values, which is preferable in a
  production financial system. For this short in-memory assignment, I used a
  positive two-decimal-place number and round calculated totals to two decimal
  places to keep the API straightforward.
