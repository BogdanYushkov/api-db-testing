# API + Database Testing Portfolio

Automated test suite for a REST API e-commerce service with database validation.

## Tech Stack

| Layer | Technology |
|-------|------------|
| API under test | FastAPI (Python) |
| Database | PostgreSQL 15 |
| Test framework | pytest |
| HTTP client | requests |
| DB client | psycopg2 |
| Auth | JWT (python-jose) |
| Reports | Allure |
| CI/CD | GitHub Actions |
| Infrastructure | Docker Compose |

## Project Structure

```
api-db-testing/
├── app/                        # API application
│   ├── main.py                 # FastAPI entry point
│   ├── database.py             # DB connection setup
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── auth.py                 # JWT authentication
│   └── routers/
│       ├── auth.py             # POST /auth/register, /auth/login
│       ├── users.py            # GET /users/, /users/{id}
│       ├── products.py         # CRUD /products/
│       └── orders.py           # CRUD /orders/
├── tests/
│   ├── conftest.py             # Shared fixtures (API client, DB, auth)
│   ├── api/
│   │   ├── test_auth.py        # Auth: register, login, token validation
│   │   ├── test_users.py       # Users: CRUD, schema validation
│   │   ├── test_products.py    # Products: CRUD, parametrized tests
│   │   └── test_orders.py      # Orders: CRUD, business logic
│   ├── db/
│   │   └── test_db_consistency.py  # API response vs DB record checks
│   └── e2e/
│       └── test_order_flow.py  # Full lifecycle: register -> order -> verify
├── docker-compose.yml
├── Dockerfile
└── .github/workflows/tests.yml
```

## What This Demonstrates

- **Functional API testing** — CRUD operations for 3 entities
- **Database validation** — direct SQL queries to verify API writes match DB state
- **Auth/Security testing** — JWT token flow, unauthorized access, invalid tokens
- **Negative testing** — 400, 401, 404, 422 error scenarios
- **Data-driven testing** — `@pytest.mark.parametrize` with multiple datasets
- **E2E flow** — complete user journey from registration to order fulfillment
- **Test isolation** — fixtures with setup/teardown for clean test state
- **CI/CD** — automated test runs on every push via GitHub Actions

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+

### Run the application

```bash
docker compose up -d --build
```

API will be available at `http://localhost:8000`.
Swagger docs at `http://localhost:8000/docs`.

### Run tests

```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Run all tests
pytest -v

# Run with Allure reporting
pytest --alluredir=allure-results -v
allure serve allure-results
```

### Environment variables

Copy `.env.example` to `.env` and adjust if needed:

```bash
cp .env.example .env
```

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /auth/register | No | Register new user |
| POST | /auth/login | No | Login, get JWT token |
| GET | /users/ | Yes | List all users |
| GET | /users/{id} | Yes | Get user by ID |
| DELETE | /users/{id} | Yes | Delete user |
| GET | /products/ | No | List all products |
| GET | /products/{id} | No | Get product by ID |
| POST | /products/ | Yes | Create product |
| PUT | /products/{id} | Yes | Update product |
| DELETE | /products/{id} | Yes | Delete product |
| GET | /orders/ | Yes | List my orders |
| GET | /orders/{id} | Yes | Get order by ID |
| POST | /orders/ | Yes | Create order |
| PUT | /orders/{id} | Yes | Update order status |
| DELETE | /orders/{id} | Yes | Delete order |
| GET | /health | No | Health check |
