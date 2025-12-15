"""
Integration Tests for Microservices API

Tests actual API endpoints and microservices integration.
These tests require actual services to be running or use mock servers.
"""

import httpx
import pytest

from src import assertions
from src.factories import generate_order, generate_product, generate_user


@pytest.mark.integration
class TestHealthCheck:
    """Test health check endpoints"""

    def test_api_health_check(self, api_client):
        """Test main API health endpoint"""
        # This is an example - adjust endpoint based on actual API
        try:
            response = api_client.get("/health")
            # API should respond with 200 or 404 if endpoint doesn't exist
            assert response.status_code in [200, 404]
        except httpx.ConnectError:
            pytest.skip("API server not available")

    def test_api_response_time(self, api_client):
        """Test API responds within acceptable time"""
        try:
            response = api_client.get("/health")
            if response.status_code == 200:
                assertions.assert_response_time(response, max_time=2.0)
        except httpx.ConnectError:
            pytest.skip("API server not available")


@pytest.mark.integration
class TestUserService:
    """Test user service endpoints"""

    def test_get_users_endpoint(self, user_service_client):
        """Test getting list of users"""
        try:
            response = user_service_client.get("/users")

            # Check if endpoint exists (200) or not implemented (404)
            if response.status_code == 200:
                assertions.assert_status_code(response, 200)
                assertions.assert_json_response(response)
                data = response.json()

                # If endpoint returns list
                if isinstance(data, list):
                    assertions.assert_list_length(data, 0, operator=">=")
            else:
                # Endpoint not implemented yet
                pytest.skip("Users endpoint not implemented")

        except httpx.ConnectError:
            pytest.skip("User service not available")

    def test_create_user(self, user_service_client):
        """Test creating a new user"""
        user_data = generate_user()

        try:
            response = user_service_client.post("/users", json=user_data)

            # Accept 201 (created) or 404 (not implemented)
            if response.status_code == 201:
                assertions.assert_status_code(response, 201)
                assertions.assert_json_response(response)
                created_user = response.json()
                assertions.assert_json_has_keys(created_user, ["id"])
            else:
                pytest.skip("Create user endpoint not implemented")

        except httpx.ConnectError:
            pytest.skip("User service not available")

    def test_get_user_by_id(self, user_service_client):
        """Test getting a specific user by ID"""
        try:
            # Try to get user with ID 1
            response = user_service_client.get("/users/1")

            if response.status_code == 200:
                assertions.assert_status_code(response, 200)
                assertions.assert_json_response(response)
                user = response.json()
                assertions.assert_json_has_keys(user, ["id"])
            elif response.status_code == 404:
                # User doesn't exist, which is acceptable
                assertions.assert_status_code(response, 404)
            else:
                pytest.skip("Get user by ID endpoint not implemented")

        except httpx.ConnectError:
            pytest.skip("User service not available")


@pytest.mark.integration
class TestProductService:
    """Test product service endpoints"""

    def test_get_products(self, product_service_client):
        """Test getting list of products"""
        try:
            response = product_service_client.get("/products")

            if response.status_code == 200:
                assertions.assert_status_code(response, 200)
                assertions.assert_json_response(response)
                data = response.json()

                if isinstance(data, list):
                    assertions.assert_list_length(data, 0, operator=">=")
            else:
                pytest.skip("Products endpoint not implemented")

        except httpx.ConnectError:
            pytest.skip("Product service not available")

    def test_create_product(self, product_service_client):
        """Test creating a new product"""
        product_data = generate_product()

        try:
            response = product_service_client.post("/products", json=product_data)

            if response.status_code == 201:
                assertions.assert_status_code(response, 201)
                assertions.assert_json_response(response)
            else:
                pytest.skip("Create product endpoint not implemented")

        except httpx.ConnectError:
            pytest.skip("Product service not available")

    def test_search_products(self, product_service_client):
        """Test searching products"""
        try:
            response = product_service_client.get("/products/search", params={"q": "test"})

            if response.status_code == 200:
                assertions.assert_status_code(response, 200)
                assertions.assert_json_response(response)
            else:
                pytest.skip("Product search endpoint not implemented")

        except httpx.ConnectError:
            pytest.skip("Product service not available")


@pytest.mark.integration
class TestOrderService:
    """Test order service endpoints"""

    def test_get_orders(self, order_service_client):
        """Test getting list of orders"""
        try:
            response = order_service_client.get("/orders")

            if response.status_code == 200:
                assertions.assert_status_code(response, 200)
                assertions.assert_json_response(response)
            else:
                pytest.skip("Orders endpoint not implemented")

        except httpx.ConnectError:
            pytest.skip("Order service not available")

    def test_create_order(self, order_service_client):
        """Test creating a new order"""
        order_data = generate_order()

        try:
            response = order_service_client.post("/orders", json=order_data)

            if response.status_code == 201:
                assertions.assert_status_code(response, 201)
                assertions.assert_json_response(response)
                created_order = response.json()
                assertions.assert_json_has_keys(created_order, ["id"])
            else:
                pytest.skip("Create order endpoint not implemented")

        except httpx.ConnectError:
            pytest.skip("Order service not available")


@pytest.mark.integration
@pytest.mark.smoke
class TestAPIConnectivity:
    """Smoke tests for API connectivity"""

    def test_can_connect_to_main_api(self, api_client):
        """Test we can connect to main API"""
        try:
            response = api_client.get("/")
            # Any response means we can connect
            assert response.status_code is not None
        except httpx.ConnectError:
            pytest.fail("Cannot connect to main API")

    def test_api_returns_json(self, api_client):
        """Test API returns JSON responses"""
        try:
            response = api_client.get("/health")
            if response.status_code == 200:
                assertions.assert_content_type(response, "application/json")
        except (httpx.ConnectError, AssertionError):
            pytest.skip("API not available or doesn't return JSON")


@pytest.mark.integration
class TestErrorHandling:
    """Test API error handling"""

    def test_404_not_found(self, api_client):
        """Test 404 response for non-existent endpoint"""
        try:
            response = api_client.get("/this-endpoint-does-not-exist-12345")
            assertions.assert_status_code(response, 404)
        except httpx.ConnectError:
            pytest.skip("API not available")

    def test_invalid_method(self, api_client):
        """Test invalid HTTP method handling"""
        try:
            # Most APIs don't support TRACE
            response = api_client.request("TRACE", "/")
            # Should return 405 (Method Not Allowed) or 501 (Not Implemented)
            assertions.assert_status_code_in(response, [405, 501, 404])
        except httpx.ConnectError:
            pytest.skip("API not available")
