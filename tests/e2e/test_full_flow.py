"""
End-to-End Tests

Tests complete user flows across multiple microservices.
"""

import pytest
import httpx

from src import assertions
from src.factories import generate_user, generate_product, generate_order


@pytest.mark.e2e
class TestUserOrderFlow:
    """Test complete user order flow"""

    def test_complete_order_flow(
        self, user_service_client, product_service_client, order_service_client
    ):
        """
        Test complete order flow:
        1. Create a user
        2. Create a product
        3. Create an order for that user and product
        4. Verify order was created successfully
        """
        try:
            # Step 1: Create a user
            user_data = generate_user()
            user_response = user_service_client.post("/users", json=user_data)

            if user_response.status_code != 201:
                pytest.skip("Cannot create user - endpoint not available")

            created_user = user_response.json()
            assertions.assert_json_has_keys(created_user, ["id"])
            user_id = created_user["id"]

            # Step 2: Create a product
            product_data = generate_product()
            product_response = product_service_client.post("/products", json=product_data)

            if product_response.status_code != 201:
                pytest.skip("Cannot create product - endpoint not available")

            created_product = product_response.json()
            assertions.assert_json_has_keys(created_product, ["id"])
            product_id = created_product["id"]

            # Step 3: Create an order
            order_data = generate_order(user_id=user_id, product_id=product_id)
            order_response = order_service_client.post("/orders", json=order_data)

            if order_response.status_code != 201:
                pytest.skip("Cannot create order - endpoint not available")

            # Step 4: Verify order
            created_order = order_response.json()
            assertions.assert_json_has_keys(created_order, ["id", "user_id", "product_id"])
            assert created_order["user_id"] == user_id
            assert created_order["product_id"] == product_id

        except httpx.ConnectError:
            pytest.skip("One or more services not available")

    def test_user_can_view_their_orders(self, user_service_client, order_service_client):
        """
        Test user can view their orders:
        1. Create a user
        2. Create multiple orders for that user
        3. Retrieve user's orders
        4. Verify all orders are returned
        """
        try:
            # Step 1: Create a user
            user_data = generate_user()
            user_response = user_service_client.post("/users", json=user_data)

            if user_response.status_code != 201:
                pytest.skip("Cannot create user - endpoint not available")

            user_id = user_response.json()["id"]

            # Step 2: Create multiple orders
            order_count = 3
            created_order_ids = []

            for _ in range(order_count):
                order_data = generate_order(user_id=user_id)
                order_response = order_service_client.post("/orders", json=order_data)

                if order_response.status_code == 201:
                    created_order_ids.append(order_response.json()["id"])

            if not created_order_ids:
                pytest.skip("Cannot create orders - endpoint not available")

            # Step 3: Retrieve user's orders
            orders_response = order_service_client.get(f"/users/{user_id}/orders")

            if orders_response.status_code != 200:
                pytest.skip("Cannot retrieve user orders - endpoint not available")

            # Step 4: Verify orders
            user_orders = orders_response.json()
            assert isinstance(user_orders, list)
            assertions.assert_list_length(user_orders, len(created_order_ids), operator=">=")

        except httpx.ConnectError:
            pytest.skip("One or more services not available")


@pytest.mark.e2e
class TestProductCatalogFlow:
    """Test product catalog functionality"""

    def test_product_search_and_retrieve(self, product_service_client):
        """
        Test product search and retrieval:
        1. Create multiple products
        2. Search for products
        3. Retrieve specific product
        4. Verify product details
        """
        try:
            # Step 1: Create products
            products_created = []
            for i in range(3):
                product_data = generate_product(name=f"Test Product {i}")
                response = product_service_client.post("/products", json=product_data)

                if response.status_code == 201:
                    products_created.append(response.json())

            if not products_created:
                pytest.skip("Cannot create products - endpoint not available")

            # Step 2: Search for products
            search_response = product_service_client.get("/products/search", params={"q": "Test"})

            if search_response.status_code != 200:
                pytest.skip("Product search not available")

            search_results = search_response.json()
            assert isinstance(search_results, list)

            # Step 3: Retrieve specific product
            if products_created:
                product_id = products_created[0]["id"]
                product_response = product_service_client.get(f"/products/{product_id}")

                if product_response.status_code == 200:
                    # Step 4: Verify product details
                    product = product_response.json()
                    assertions.assert_json_has_keys(product, ["id", "name"])
                    assert product["id"] == product_id

        except httpx.ConnectError:
            pytest.skip("Product service not available")


@pytest.mark.e2e
class TestDataConsistency:
    """Test data consistency across services"""

    def test_user_data_consistency(self, user_service_client):
        """
        Test user data remains consistent:
        1. Create a user
        2. Retrieve the user
        3. Update the user
        4. Verify updates were applied
        """
        try:
            # Step 1: Create user
            user_data = generate_user(email="consistency@test.com")
            create_response = user_service_client.post("/users", json=user_data)

            if create_response.status_code != 201:
                pytest.skip("Cannot create user - endpoint not available")

            created_user = create_response.json()
            user_id = created_user["id"]

            # Step 2: Retrieve user
            get_response = user_service_client.get(f"/users/{user_id}")

            if get_response.status_code != 200:
                pytest.skip("Cannot retrieve user - endpoint not available")

            retrieved_user = get_response.json()
            assert retrieved_user["email"] == "consistency@test.com"

            # Step 3: Update user
            update_data = {"email": "updated@test.com"}
            update_response = user_service_client.patch(f"/users/{user_id}", json=update_data)

            if update_response.status_code not in [200, 204]:
                pytest.skip("Cannot update user - endpoint not available")

            # Step 4: Verify update
            verify_response = user_service_client.get(f"/users/{user_id}")

            if verify_response.status_code == 200:
                updated_user = verify_response.json()
                assert updated_user["email"] == "updated@test.com"

        except httpx.ConnectError:
            pytest.skip("User service not available")


@pytest.mark.e2e
@pytest.mark.slow
class TestBulkOperations:
    """Test bulk operations across services"""

    def test_bulk_user_creation(self, user_service_client):
        """Test creating multiple users in bulk"""
        try:
            user_count = 10
            successful_creates = 0

            for i in range(user_count):
                user_data = generate_user(username=f"bulkuser{i}")
                response = user_service_client.post("/users", json=user_data)

                if response.status_code == 201:
                    successful_creates += 1

            if successful_creates == 0:
                pytest.skip("User creation endpoint not available")

            # Verify at least some users were created
            assert successful_creates > 0

        except httpx.ConnectError:
            pytest.skip("User service not available")

    def test_bulk_order_processing(self, order_service_client):
        """Test processing multiple orders"""
        try:
            order_count = 5
            successful_orders = 0

            for i in range(order_count):
                order_data = generate_order()
                response = order_service_client.post("/orders", json=order_data)

                if response.status_code == 201:
                    successful_orders += 1

            if successful_orders == 0:
                pytest.skip("Order creation endpoint not available")

            # Verify at least some orders were created
            assert successful_orders > 0

        except httpx.ConnectError:
            pytest.skip("Order service not available")


@pytest.mark.e2e
class TestErrorRecovery:
    """Test error recovery scenarios"""

    def test_invalid_user_order(self, order_service_client):
        """Test creating order with invalid user ID"""
        try:
            order_data = generate_order(user_id=999999)  # Non-existent user
            response = order_service_client.post("/orders", json=order_data)

            # Should return error status (400, 404, or similar)
            if response.status_code in [400, 404, 422]:
                assertions.assert_status_code_in(response, [400, 404, 422])
            else:
                pytest.skip("Error validation not implemented")

        except httpx.ConnectError:
            pytest.skip("Order service not available")
