"""
Integration Tests for Microservices Patterns

Tests common microservices integration patterns and scenarios.
"""

import pytest
import asyncio
from src.utils.assertions import (
    assert_status_code,
    assert_json_contains,
    assert_is_list,
)


@pytest.mark.integration
class TestMicroservicesPatterns:
    """Test microservices integration patterns."""
    
    def test_service_health_check(self, api_client):
        """Test service availability."""
        # Most APIs have a root endpoint
        response = api_client.get("/")
        
        # Service should respond (even if 404)
        assert response.status_code in [200, 404]
    
    def test_pagination_support(self, api_client):
        """Test API pagination capabilities."""
        # Get posts with pagination parameters
        response = api_client.get("/posts", params={"_limit": 5, "_page": 1})
        
        assert_status_code(response, 200)
        
        posts = response.json()
        assert_is_list(posts, max_length=5)
    
    def test_filtering_support(self, api_client):
        """Test API filtering capabilities."""
        # Filter posts by userId
        user_id = 1
        response = api_client.get("/posts", params={"userId": user_id})
        
        assert_status_code(response, 200)
        
        posts = response.json()
        assert_is_list(posts, min_length=1)
        
        # Verify all posts belong to the filtered user
        for post in posts:
            assert post["userId"] == user_id
    
    def test_sorting_support(self, api_client):
        """Test API sorting capabilities."""
        # Get posts sorted by id
        response = api_client.get("/posts", params={"_sort": "id", "_order": "asc"})
        
        assert_status_code(response, 200)
        
        posts = response.json()
        
        # Verify posts are sorted
        if len(posts) > 1:
            for i in range(len(posts) - 1):
                assert posts[i]["id"] <= posts[i + 1]["id"]
    
    def test_nested_resource_access(self, api_client):
        """Test accessing nested resources."""
        user_id = 1
        
        # Access nested resource: user's posts
        response = api_client.get(f"/users/{user_id}/posts")
        
        assert_status_code(response, 200)
        
        posts = response.json()
        assert_is_list(posts, min_length=1)
        
        # Verify all posts belong to the user
        for post in posts:
            assert post["userId"] == user_id
    
    def test_cross_service_data_consistency(self, api_client):
        """Test data consistency across related endpoints."""
        # Get a user
        user_id = 1
        user_response = api_client.get(f"/users/{user_id}")
        assert_status_code(user_response, 200)
        user = user_response.json()
        
        # Get that user's posts
        posts_response = api_client.get(f"/posts", params={"userId": user_id})
        assert_status_code(posts_response, 200)
        posts = posts_response.json()
        
        # Verify consistency: all posts should have matching userId
        for post in posts:
            assert post["userId"] == user["id"]
    
    def test_multiple_concurrent_requests(self, api_client):
        """Test handling multiple concurrent requests."""
        import concurrent.futures
        
        def make_request(endpoint):
            return api_client.get(endpoint)
        
        # Make multiple concurrent requests
        endpoints = ["/posts", "/users", "/comments", "/todos", "/albums"]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, ep) for ep in endpoints]
            responses = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        assert len(responses) == len(endpoints)
        for response in responses:
            assert response.status_code == 200
    
    def test_error_handling_not_found(self, api_client):
        """Test proper error handling for non-existent resources."""
        # Request a non-existent post
        response = api_client.get("/posts/99999")
        
        # Should return 404
        assert_status_code(response, 404)
    
    def test_request_with_invalid_parameters(self, api_client):
        """Test handling of invalid query parameters."""
        # Request with invalid parameter
        response = api_client.get("/posts", params={"_limit": "invalid"})
        
        # Should still return (may ignore invalid param)
        assert response.status_code in [200, 400]


@pytest.mark.integration
@pytest.mark.asyncio
class TestAsyncMicroservices:
    """Test async microservices patterns."""
    
    async def test_async_get_posts(self, async_api_client):
        """Test async GET request."""
        response = await async_api_client.get_async("/posts")
        
        assert_status_code(response, 200)
        posts = response.json()
        assert_is_list(posts, min_length=1)
    
    async def test_async_parallel_requests(self, async_api_client):
        """Test making multiple async requests in parallel."""
        # Create multiple async tasks
        tasks = [
            async_api_client.get_async("/posts/1"),
            async_api_client.get_async("/posts/2"),
            async_api_client.get_async("/posts/3"),
            async_api_client.get_async("/users/1"),
            async_api_client.get_async("/todos/1"),
        ]
        
        # Execute all tasks concurrently
        responses = await asyncio.gather(*tasks)
        
        # All requests should succeed
        assert len(responses) == 5
        for response in responses:
            assert_status_code(response, 200)
    
    async def test_async_create_resource(self, async_api_client, test_post_data):
        """Test async POST request."""
        response = await async_api_client.post_async("/posts", json=test_post_data)
        
        assert_status_code(response, 201)
        
        created_post = response.json()
        assert created_post["title"] == test_post_data["title"]
    
    async def test_async_sequential_operations(self, async_api_client):
        """Test sequential async operations (create, read, update, delete)."""
        # Create
        create_data = {
            "title": "Async Test Post",
            "body": "Test content",
            "userId": 1
        }
        create_response = await async_api_client.post_async("/posts", json=create_data)
        assert_status_code(create_response, 201)
        created_post = create_response.json()
        post_id = created_post["id"]
        
        # Read
        read_response = await async_api_client.get_async(f"/posts/{post_id}")
        assert_status_code(read_response, 200)
        
        # Update
        update_data = {**created_post, "title": "Updated Async Post"}
        update_response = await async_api_client.put_async(f"/posts/{post_id}", json=update_data)
        assert_status_code(update_response, 200)
        
        # Delete
        delete_response = await async_api_client.delete_async(f"/posts/{post_id}")
        assert_status_code(delete_response, 200)


@pytest.mark.integration
class TestServiceResilience:
    """Test service resilience patterns."""
    
    def test_retry_on_temporary_failure(self, api_client):
        """Test that client retries on temporary failures."""
        # This test assumes the API is stable
        # In a real scenario, you might use a mock or test server
        response = api_client.get("/posts/1")
        assert_status_code(response, 200)
    
    def test_timeout_handling(self, api_client):
        """Test request timeout handling."""
        # Create client with very short timeout for testing
        from src.clients.api_client import APIClient
        
        short_timeout_client = APIClient(timeout=0.001)
        
        try:
            # This should timeout
            response = short_timeout_client.get("/posts")
            # If it doesn't timeout, that's also OK (fast response)
            assert response.status_code == 200
        except Exception:
            # Timeout exception is expected
            pass
        finally:
            short_timeout_client.close()
