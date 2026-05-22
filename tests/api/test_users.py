import requests


class TestGetUsers:
    def test_get_all_users(self, api_url, auth_header):
        """Test GET /users/ returns list of users."""
        resp = requests.get(f"{api_url}/users/", headers=auth_header)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_user_by_id(self, api_url, auth_header, test_user):
        """Test GET /users/{id} returns correct user."""
        all_users = requests.get(f"{api_url}/users/", headers=auth_header).json()
        user = next(u for u in all_users if u["username"] == test_user["username"])

        resp = requests.get(f"{api_url}/users/{user['id']}", headers=auth_header)
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == test_user["username"]
        assert data["email"] == test_user["email"]

    def test_get_nonexistent_user(self, api_url, auth_header):
        """Test GET /users/{id} with invalid id returns 404."""
        resp = requests.get(f"{api_url}/users/99999", headers=auth_header)
        assert resp.status_code == 404

    def test_get_users_without_auth(self, api_url):
        """Test GET /users/ without auth returns 401."""
        resp = requests.get(f"{api_url}/users/")
        assert resp.status_code == 401


class TestUserResponseSchema:
    def test_user_response_has_required_fields(self, api_url, auth_header):
        """Test user response contains all required fields."""
        resp = requests.get(f"{api_url}/users/", headers=auth_header)
        assert resp.status_code == 200
        users = resp.json()
        if users:
            user = users[0]
            assert "id" in user
            assert "username" in user
            assert "email" in user
            assert "created_at" in user
            assert "hashed_password" not in user
