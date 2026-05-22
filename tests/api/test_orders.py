import requests


class TestCreateOrder:
    def test_create_order(self, api_url, auth_header, test_product):
        """Test POST /orders/ creates order successfully."""
        order_data = {"product_id": test_product["id"], "quantity": 2}
        resp = requests.post(f"{api_url}/orders/", json=order_data, headers=auth_header)
        assert resp.status_code == 201
        data = resp.json()
        assert data["product_id"] == test_product["id"]
        assert data["quantity"] == 2
        assert data["total_price"] == test_product["price"] * 2
        assert data["status"] == "pending"

    def test_create_order_insufficient_stock(self, api_url, auth_header, test_product):
        """Test POST /orders/ with quantity > stock returns 400."""
        order_data = {"product_id": test_product["id"], "quantity": 99999}
        resp = requests.post(f"{api_url}/orders/", json=order_data, headers=auth_header)
        assert resp.status_code == 400
        assert "stock" in resp.json()["detail"].lower()

    def test_create_order_nonexistent_product(self, api_url, auth_header):
        """Test POST /orders/ with invalid product_id returns 404."""
        order_data = {"product_id": 99999, "quantity": 1}
        resp = requests.post(f"{api_url}/orders/", json=order_data, headers=auth_header)
        assert resp.status_code == 404

    def test_create_order_without_auth(self, api_url, test_product):
        """Test POST /orders/ without auth returns 401."""
        order_data = {"product_id": test_product["id"], "quantity": 1}
        resp = requests.post(f"{api_url}/orders/", json=order_data)
        assert resp.status_code == 401

    def test_create_order_missing_fields(self, api_url, auth_header):
        """Test POST /orders/ with missing fields returns 422."""
        resp = requests.post(f"{api_url}/orders/", json={}, headers=auth_header)
        assert resp.status_code == 422


class TestGetOrders:
    def test_get_my_orders(self, api_url, auth_header):
        """Test GET /orders/ returns current user's orders."""
        resp = requests.get(f"{api_url}/orders/", headers=auth_header)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_orders_without_auth(self, api_url):
        """Test GET /orders/ without auth returns 401."""
        resp = requests.get(f"{api_url}/orders/")
        assert resp.status_code == 401


class TestUpdateOrder:
    def test_update_order_status(self, api_url, auth_header, test_product):
        """Test PUT /orders/{id} updates order status."""
        order_data = {"product_id": test_product["id"], "quantity": 1}
        create_resp = requests.post(
            f"{api_url}/orders/", json=order_data, headers=auth_header
        )
        order_id = create_resp.json()["id"]

        resp = requests.put(
            f"{api_url}/orders/{order_id}",
            json={"status": "confirmed"},
            headers=auth_header,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "confirmed"

    def test_update_nonexistent_order(self, api_url, auth_header):
        """Test PUT /orders/{id} with invalid id returns 404."""
        resp = requests.put(
            f"{api_url}/orders/99999",
            json={"status": "confirmed"},
            headers=auth_header,
        )
        assert resp.status_code == 404
