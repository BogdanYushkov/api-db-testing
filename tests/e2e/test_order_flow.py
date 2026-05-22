import pytest
import requests


@pytest.mark.e2e
class TestOrderFlow:
    """End-to-end test: register -> login -> create product -> place order -> verify in DB."""

    def test_full_order_lifecycle(self, api_url, db_cursor):
        """Test complete order flow from registration to order verification."""
        # Step 1: Register a new user
        user_data = {
            "username": "e2e_user",
            "email": "e2e_user@example.com",
            "password": "E2EPass123!",
        }
        reg_resp = requests.post(f"{api_url}/auth/register", json=user_data)
        assert reg_resp.status_code in (201, 400)

        # Step 2: Login
        login_resp = requests.post(
            f"{api_url}/auth/login",
            json={"username": user_data["username"], "password": user_data["password"]},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 3: Create a product
        product_data = {
            "name": "E2E Product",
            "description": "End-to-end test product",
            "price": 25.00,
            "stock": 10,
        }
        product_resp = requests.post(
            f"{api_url}/products/", json=product_data, headers=headers
        )
        assert product_resp.status_code == 201
        product_id = product_resp.json()["id"]

        # Step 4: Place an order
        order_data = {"product_id": product_id, "quantity": 3}
        order_resp = requests.post(
            f"{api_url}/orders/", json=order_data, headers=headers
        )
        assert order_resp.status_code == 201
        order = order_resp.json()
        order_id = order["id"]
        assert order["total_price"] == 75.00
        assert order["status"] == "pending"

        # Step 5: Update order status
        update_resp = requests.put(
            f"{api_url}/orders/{order_id}",
            json={"status": "confirmed"},
            headers=headers,
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["status"] == "confirmed"

        # Step 6: Verify order in database
        db_cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        db_order = db_cursor.fetchone()
        assert db_order is not None
        assert db_order["status"] == "confirmed"
        assert float(db_order["total_price"]) == 75.00

        # Step 7: Verify stock was decremented
        db_cursor.execute("SELECT stock FROM products WHERE id = %s", (product_id,))
        assert db_cursor.fetchone()["stock"] == 7

        # Step 8: Verify order appears in user's orders list
        orders_resp = requests.get(f"{api_url}/orders/", headers=headers)
        assert orders_resp.status_code == 200
        user_orders = orders_resp.json()
        assert any(o["id"] == order_id for o in user_orders)

        # Cleanup
        requests.delete(f"{api_url}/orders/{order_id}", headers=headers)
        requests.delete(f"{api_url}/products/{product_id}", headers=headers)
