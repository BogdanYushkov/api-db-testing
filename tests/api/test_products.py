import pytest
import requests


class TestGetProducts:
    def test_get_all_products(self, api_url):
        """Test GET /products/ returns list."""
        resp = requests.get(f"{api_url}/products/")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_product_by_id(self, api_url, test_product):
        """Test GET /products/{id} returns correct product."""
        resp = requests.get(f"{api_url}/products/{test_product['id']}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == test_product["id"]
        assert data["name"] == test_product["name"]

    def test_get_nonexistent_product(self, api_url):
        """Test GET /products/{id} with invalid id returns 404."""
        resp = requests.get(f"{api_url}/products/99999")
        assert resp.status_code == 404


class TestCreateProduct:
    def test_create_product(self, api_url, auth_header):
        """Test POST /products/ creates product successfully."""
        product_data = {
            "name": "New Product",
            "description": "Brand new",
            "price": 49.99,
            "stock": 50,
        }
        resp = requests.post(f"{api_url}/products/", json=product_data, headers=auth_header)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == product_data["name"]
        assert data["price"] == product_data["price"]
        assert "id" in data
        # Cleanup
        requests.delete(f"{api_url}/products/{data['id']}", headers=auth_header)

    def test_create_product_without_auth(self, api_url):
        """Test POST /products/ without auth returns 401."""
        product_data = {"name": "Unauthorized", "price": 10.0, "stock": 5}
        resp = requests.post(f"{api_url}/products/", json=product_data)
        assert resp.status_code == 401

    def test_create_product_missing_required_fields(self, api_url, auth_header):
        """Test POST /products/ with missing fields returns 422."""
        resp = requests.post(f"{api_url}/products/", json={}, headers=auth_header)
        assert resp.status_code == 422

    @pytest.mark.parametrize(
        "name, price, stock",
        [
            ("Budget Item", 0.01, 1),
            ("Expensive Item", 99999.99, 1000),
            ("Free Stock Item", 5.0, 0),
        ],
        ids=["min_price", "high_price", "zero_stock"],
    )
    def test_create_product_parametrized(self, api_url, auth_header, name, price, stock):
        """Test creating products with various valid data combinations."""
        product_data = {"name": name, "price": price, "stock": stock}
        resp = requests.post(f"{api_url}/products/", json=product_data, headers=auth_header)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == name
        assert data["price"] == price
        # Cleanup
        requests.delete(f"{api_url}/products/{data['id']}", headers=auth_header)


class TestUpdateProduct:
    def test_update_product(self, api_url, auth_header, test_product):
        """Test PUT /products/{id} updates product."""
        update_data = {"name": "Updated Product", "price": 39.99}
        resp = requests.put(
            f"{api_url}/products/{test_product['id']}",
            json=update_data,
            headers=auth_header,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Updated Product"
        assert data["price"] == 39.99

    def test_update_nonexistent_product(self, api_url, auth_header):
        """Test PUT /products/{id} with invalid id returns 404."""
        resp = requests.put(
            f"{api_url}/products/99999",
            json={"name": "Ghost"},
            headers=auth_header,
        )
        assert resp.status_code == 404


class TestDeleteProduct:
    def test_delete_product(self, api_url, auth_header):
        """Test DELETE /products/{id} removes product."""
        product_data = {"name": "To Delete", "price": 10.0, "stock": 1}
        create_resp = requests.post(
            f"{api_url}/products/", json=product_data, headers=auth_header
        )
        product_id = create_resp.json()["id"]

        resp = requests.delete(f"{api_url}/products/{product_id}", headers=auth_header)
        assert resp.status_code == 204

        get_resp = requests.get(f"{api_url}/products/{product_id}")
        assert get_resp.status_code == 404

    def test_delete_nonexistent_product(self, api_url, auth_header):
        """Test DELETE /products/{id} with invalid id returns 404."""
        resp = requests.delete(f"{api_url}/products/99999", headers=auth_header)
        assert resp.status_code == 404
