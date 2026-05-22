import os

import psycopg2
import pytest
import requests
from psycopg2.extras import RealDictCursor

API_URL = os.getenv("API_URL", "http://localhost:8000")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "testdb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")


@pytest.fixture(scope="session")
def api_url():
    return API_URL


@pytest.fixture(scope="session")
def db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )
    yield conn
    conn.close()


@pytest.fixture
def db_cursor(db_connection):
    cursor = db_connection.cursor(cursor_factory=RealDictCursor)
    yield cursor
    db_connection.rollback()


@pytest.fixture(scope="session")
def test_user(api_url):
    """Register a test user and return credentials + token."""
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "TestPass123!",
    }
    resp = requests.post(f"{api_url}/auth/register", json=user_data)
    if resp.status_code not in (201, 400):
        resp.raise_for_status()

    login_resp = requests.post(
        f"{api_url}/auth/login",
        json={"username": user_data["username"], "password": user_data["password"]},
    )
    login_resp.raise_for_status()
    token = login_resp.json()["access_token"]

    return {
        "username": user_data["username"],
        "email": user_data["email"],
        "password": user_data["password"],
        "token": token,
    }


@pytest.fixture(scope="session")
def auth_header(test_user):
    return {"Authorization": f"Bearer {test_user['token']}"}


@pytest.fixture
def test_product(api_url, auth_header):
    """Create a test product and clean up after test."""
    product_data = {
        "name": "Test Product",
        "description": "A product for testing",
        "price": 29.99,
        "stock": 100,
    }
    resp = requests.post(f"{api_url}/products/", json=product_data, headers=auth_header)
    resp.raise_for_status()
    product = resp.json()
    yield product
    requests.delete(f"{api_url}/products/{product['id']}", headers=auth_header)
