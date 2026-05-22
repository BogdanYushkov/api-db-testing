import requests


class TestAuthRegister:
    def test_register_new_user(self, api_url):
        """Test successful user registration."""
        user_data = {
            "username": "newuser_reg",
            "email": "newuser_reg@example.com",
            "password": "StrongPass123!",
        }
        resp = requests.post(f"{api_url}/auth/register", json=user_data)
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "id" in data
        assert "hashed_password" not in data

    def test_register_duplicate_username(self, api_url, test_user):
        """Test registration with existing username returns 400."""
        user_data = {
            "username": test_user["username"],
            "email": "different@example.com",
            "password": "SomePass123!",
        }
        resp = requests.post(f"{api_url}/auth/register", json=user_data)
        assert resp.status_code == 400
        assert "already exists" in resp.json()["detail"].lower()

    def test_register_duplicate_email(self, api_url, test_user):
        """Test registration with existing email returns 400."""
        user_data = {
            "username": "differentuser",
            "email": test_user["email"],
            "password": "SomePass123!",
        }
        resp = requests.post(f"{api_url}/auth/register", json=user_data)
        assert resp.status_code == 400

    def test_register_invalid_email(self, api_url):
        """Test registration with invalid email returns 422."""
        user_data = {
            "username": "invalidemail",
            "email": "not-an-email",
            "password": "SomePass123!",
        }
        resp = requests.post(f"{api_url}/auth/register", json=user_data)
        assert resp.status_code == 422

    def test_register_missing_fields(self, api_url):
        """Test registration with missing fields returns 422."""
        resp = requests.post(f"{api_url}/auth/register", json={})
        assert resp.status_code == 422


class TestAuthLogin:
    def test_login_valid_credentials(self, api_url, test_user):
        """Test login with valid credentials returns token."""
        resp = requests.post(
            f"{api_url}/auth/login",
            json={"username": test_user["username"], "password": test_user["password"]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, api_url, test_user):
        """Test login with wrong password returns 401."""
        resp = requests.post(
            f"{api_url}/auth/login",
            json={"username": test_user["username"], "password": "wrongpassword"},
        )
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, api_url):
        """Test login with non-existent user returns 401."""
        resp = requests.post(
            f"{api_url}/auth/login",
            json={"username": "nonexistent", "password": "SomePass123!"},
        )
        assert resp.status_code == 401


class TestAuthProtection:
    def test_access_without_token(self, api_url):
        """Test accessing protected endpoint without token returns 401."""
        resp = requests.get(f"{api_url}/users/")
        assert resp.status_code == 401

    def test_access_with_invalid_token(self, api_url):
        """Test accessing protected endpoint with invalid token returns 401."""
        headers = {"Authorization": "Bearer invalidtoken123"}
        resp = requests.get(f"{api_url}/users/", headers=headers)
        assert resp.status_code == 401

    def test_access_with_expired_token(self, api_url):
        """Test accessing protected endpoint with expired token returns 401."""
        expired_token = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTAwMDAwMDAwMH0."
            "invalid_signature"
        )
        headers = {"Authorization": f"Bearer {expired_token}"}
        resp = requests.get(f"{api_url}/users/", headers=headers)
        assert resp.status_code == 401
