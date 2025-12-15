"""
Integration Tests for API Endpoints

Tests individual API endpoints to ensure they work correctly.
Uses JSONPlaceholder API as an example.
"""

import pytest
from src.utils.assertions import (
    assert_status_code,
    assert_response_time,
    assert_json_contains,
    assert_is_list,
    assert_successful_response,
)
from src.validators.schema_validator import COMMON_SCHEMAS


@pytest.mark.integration
class TestPostsEndpoint:
    """Test cases for /posts endpoint."""
    
    def test_get_all_posts(self, api_client, schema_validator):
        """Test retrieving all posts."""
        response = api_client.get("/posts")
        
        # Assert successful response
        assert_successful_response(response)
        assert_status_code(response, 200)
        
        # Assert response time
        assert_response_time(response, max_time_seconds=3.0)
        
        # Parse JSON
        posts = response.json()
        
        # Assert response is a list
        assert_is_list(posts, min_length=1)
        
        # Validate first post schema
        if posts:
            schema_validator.validate(posts[0], COMMON_SCHEMAS["post"])
    
    def test_get_post_by_id(self, api_client, schema_validator):
        """Test retrieving a specific post by ID."""
        post_id = 1
        response = api_client.get(f"/posts/{post_id}")
        
        # Assert successful response
        assert_status_code(response, 200)
        assert_response_time(response, max_time_seconds=2.0)
        
        # Parse JSON
        post = response.json()
        
        # Assert required fields
        assert_json_contains(post, ["userId", "id", "title", "body"])
        
        # Validate schema
        schema_validator.validate(post, COMMON_SCHEMAS["post"])
        
        # Assert correct post ID
        assert post["id"] == post_id
    
    def test_create_post(self, api_client, test_post_data):
        """Test creating a new post."""
        response = api_client.post("/posts", json=test_post_data)
        
        # Assert successful creation
        assert_status_code(response, 201)
        
        # Parse JSON
        created_post = response.json()
        
        # Assert created post contains submitted data
        assert created_post["title"] == test_post_data["title"]
        assert created_post["body"] == test_post_data["body"]
        assert created_post["userId"] == test_post_data["userId"]
        
        # Assert ID was assigned
        assert "id" in created_post
    
    def test_update_post(self, api_client):
        """Test updating an existing post."""
        post_id = 1
        update_data = {
            "id": post_id,
            "title": "Updated Title",
            "body": "Updated body content",
            "userId": 1
        }
        
        response = api_client.put(f"/posts/{post_id}", json=update_data)
        
        # Assert successful update
        assert_status_code(response, 200)
        
        # Parse JSON
        updated_post = response.json()
        
        # Assert data was updated
        assert updated_post["title"] == update_data["title"]
        assert updated_post["body"] == update_data["body"]
    
    def test_patch_post(self, api_client):
        """Test partially updating a post."""
        post_id = 1
        patch_data = {
            "title": "Patched Title"
        }
        
        response = api_client.patch(f"/posts/{post_id}", json=patch_data)
        
        # Assert successful patch
        assert_status_code(response, 200)
        
        # Parse JSON
        patched_post = response.json()
        
        # Assert title was updated
        assert patched_post["title"] == patch_data["title"]
    
    def test_delete_post(self, api_client):
        """Test deleting a post."""
        post_id = 1
        response = api_client.delete(f"/posts/{post_id}")
        
        # Assert successful deletion
        assert_status_code(response, 200)


@pytest.mark.integration
class TestUsersEndpoint:
    """Test cases for /users endpoint."""
    
    def test_get_all_users(self, api_client, schema_validator):
        """Test retrieving all users."""
        response = api_client.get("/users")
        
        # Assert successful response
        assert_status_code(response, 200)
        assert_response_time(response, max_time_seconds=3.0)
        
        # Parse JSON
        users = response.json()
        
        # Assert response is a list
        assert_is_list(users, min_length=1)
        
        # Validate schema for all users
        schema_validator.validate_list(users, COMMON_SCHEMAS["user"])
    
    def test_get_user_by_id(self, api_client, schema_validator):
        """Test retrieving a specific user by ID."""
        user_id = 1
        response = api_client.get(f"/users/{user_id}")
        
        # Assert successful response
        assert_status_code(response, 200)
        
        # Parse JSON
        user = response.json()
        
        # Assert required fields
        assert_json_contains(user, ["id", "name", "email", "username"])
        
        # Validate schema
        schema_validator.validate(user, COMMON_SCHEMAS["user"])
        
        # Assert correct user ID
        assert user["id"] == user_id
    
    def test_get_user_posts(self, api_client):
        """Test retrieving posts for a specific user."""
        user_id = 1
        response = api_client.get(f"/users/{user_id}/posts")
        
        # Assert successful response
        assert_status_code(response, 200)
        
        # Parse JSON
        posts = response.json()
        
        # Assert response is a list
        assert_is_list(posts, min_length=1)
        
        # Assert all posts belong to the user
        for post in posts:
            assert post["userId"] == user_id


@pytest.mark.integration
class TestCommentsEndpoint:
    """Test cases for /comments endpoint."""
    
    def test_get_all_comments(self, api_client):
        """Test retrieving all comments."""
        response = api_client.get("/comments")
        
        # Assert successful response
        assert_status_code(response, 200)
        
        # Parse JSON
        comments = response.json()
        
        # Assert response is a list
        assert_is_list(comments, min_length=1)
    
    def test_get_comments_by_post(self, api_client, schema_validator):
        """Test retrieving comments for a specific post."""
        post_id = 1
        response = api_client.get("/comments", params={"postId": post_id})
        
        # Assert successful response
        assert_status_code(response, 200)
        
        # Parse JSON
        comments = response.json()
        
        # Assert response is a list
        assert_is_list(comments, min_length=1)
        
        # Validate first comment schema
        if comments:
            schema_validator.validate(comments[0], COMMON_SCHEMAS["comment"])
        
        # Assert all comments belong to the post
        for comment in comments:
            assert comment["postId"] == post_id


@pytest.mark.integration
class TestTodosEndpoint:
    """Test cases for /todos endpoint."""
    
    def test_get_all_todos(self, api_client):
        """Test retrieving all todos."""
        response = api_client.get("/todos")
        
        # Assert successful response
        assert_status_code(response, 200)
        
        # Parse JSON
        todos = response.json()
        
        # Assert response is a list
        assert_is_list(todos, min_length=1)
    
    def test_get_todo_by_id(self, api_client, schema_validator):
        """Test retrieving a specific todo by ID."""
        todo_id = 1
        response = api_client.get(f"/todos/{todo_id}")
        
        # Assert successful response
        assert_status_code(response, 200)
        
        # Parse JSON
        todo = response.json()
        
        # Assert required fields
        assert_json_contains(todo, ["userId", "id", "title", "completed"])
        
        # Validate schema
        schema_validator.validate(todo, COMMON_SCHEMAS["todo"])
        
        # Assert correct todo ID
        assert todo["id"] == todo_id
    
    def test_create_todo(self, api_client, test_todo_data):
        """Test creating a new todo."""
        response = api_client.post("/todos", json=test_todo_data)
        
        # Assert successful creation
        assert_status_code(response, 201)
        
        # Parse JSON
        created_todo = response.json()
        
        # Assert created todo contains submitted data
        assert created_todo["title"] == test_todo_data["title"]
        assert created_todo["completed"] == test_todo_data["completed"]
