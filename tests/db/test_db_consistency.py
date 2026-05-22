import requests


class TestUserDBConsistency:
    def test_registered_user_exists_in_db(self, api_url, db_cursor):
        """Test that a user registered via API exists in the database."""
        user_data = {
            "username": "db_check_user",
            "email": "db_check@example.com",
            "password": "DbCheckPass123!",
        }
        resp = requests.post(f"{api_url}/auth/register", json=user_data)
        if resp.status_code == 201:
            user_id = resp.json()["id"]
        else:
            db_cursor.execute(
                "SELECT id FROM users WHERE username = %s", (user_data["username"],)
            )
            user_id = db_cursor.fetchone()["id"]

        db_cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        db_user = db_cursor.fetchone()

        assert db_user is not None
        assert db_user["username"] == user_data["username"]
        assert db_user["email"] == user_data["email"]
        assert db_user["hashed_password"] != user_data["password"]


class TestProductDBConsistency:
    def test_created_product_exists_in_db(self, api_url, auth_header, db_cursor):
        """Test that a product created via API exists in the database."""
        product_data = {
            "name": "DB Check Product",
            "description": "For DB verification",
            "price": 15.99,
            "stock": 25,
        }
        resp = requests.post(
            f"{api_url}/products/", json=product_data, headers=auth_header
        )
        assert resp.status_code == 201
        product_id = resp.json()["id"]

        db_cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        db_product = db_cursor.fetchone()

        assert db_product is not None
        assert db_product["name"] == product_data["name"]
        assert float(db_product["price"]) == product_data["price"]
        assert db_product["stock"] == product_data["stock"]

        # Cleanup
        requests.delete(f"{api_url}/products/{product_id}", headers=auth_header)

    def test_deleted_product_removed_from_db(self, api_url, auth_header, db_cursor):
        """Test that a deleted product is removed from the database."""
        product_data = {"name": "To Be Deleted", "price": 5.0, "stock": 1}
        resp = requests.post(
            f"{api_url}/products/", json=product_data, headers=auth_header
        )
        product_id = resp.json()["id"]

        requests.delete(f"{api_url}/products/{product_id}", headers=auth_header)

        db_cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        assert db_cursor.fetchone() is None


class TestOrderDBConsistency:
    def test_order_stored_correctly_in_db(self, api_url, auth_header, test_product, db_cursor):
        """Test that an order created via API is stored correctly in DB."""
        order_data = {"product_id": test_product["id"], "quantity": 3}
        resp = requests.post(
            f"{api_url}/orders/", json=order_data, headers=auth_header
        )
        assert resp.status_code == 201
        order_id = resp.json()["id"]

        db_cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        db_order = db_cursor.fetchone()

        assert db_order is not None
        assert db_order["product_id"] == test_product["id"]
        assert db_order["quantity"] == 3
        assert float(db_order["total_price"]) == test_product["price"] * 3
        assert db_order["status"] == "pending"

    def test_stock_decremented_after_order(self, api_url, auth_header, db_cursor):
        """Test that product stock is decremented in DB after order creation."""
        product_data = {"name": "Stock Test", "price": 10.0, "stock": 50}
        product_resp = requests.post(
            f"{api_url}/products/", json=product_data, headers=auth_header
        )
        product_id = product_resp.json()["id"]

        order_data = {"product_id": product_id, "quantity": 5}
        requests.post(f"{api_url}/orders/", json=order_data, headers=auth_header)

        db_cursor.execute("SELECT stock FROM products WHERE id = %s", (product_id,))
        remaining_stock = db_cursor.fetchone()["stock"]
        assert remaining_stock == 45

        # Cleanup
        requests.delete(f"{api_url}/products/{product_id}", headers=auth_header)
