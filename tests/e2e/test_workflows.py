"""
End-to-End Workflow Tests

Tests complete workflows involving multiple API calls and operations.
"""

import pytest
from src.utils.assertions import (
    assert_status_code,
    assert_json_contains,
    assert_is_list,
)


@pytest.mark.e2e
class TestUserWorkflows:
    """Test complete user-related workflows."""
    
    def test_user_and_posts_workflow(self, api_client):
        """Test workflow: Get user -> Get user's posts -> Get post comments."""
        # Step 1: Get a user
        user_id = 1
        user_response = api_client.get(f"/users/{user_id}")
        assert_status_code(user_response, 200)
        
        user = user_response.json()
        assert_json_contains(user, ["id", "name", "email"])
        
        # Step 2: Get user's posts
        posts_response = api_client.get(f"/posts", params={"userId": user_id})
        assert_status_code(posts_response, 200)
        
        posts = posts_response.json()
        assert_is_list(posts, min_length=1)
        
        # Step 3: Get comments for first post
        first_post_id = posts[0]["id"]
        comments_response = api_client.get(f"/comments", params={"postId": first_post_id})
        assert_status_code(comments_response, 200)
        
        comments = comments_response.json()
        assert_is_list(comments, min_length=1)
        
        # Verify workflow data consistency
        assert user["id"] == user_id
        for post in posts:
            assert post["userId"] == user_id
        for comment in comments:
            assert comment["postId"] == first_post_id
    
    def test_user_todos_workflow(self, api_client):
        """Test workflow: Get user -> Get user's todos -> Filter completed."""
        # Step 1: Get a user
        user_id = 1
        user_response = api_client.get(f"/users/{user_id}")
        assert_status_code(user_response, 200)
        
        # Step 2: Get user's todos
        todos_response = api_client.get(f"/todos", params={"userId": user_id})
        assert_status_code(todos_response, 200)
        
        todos = todos_response.json()
        assert_is_list(todos, min_length=1)
        
        # Step 3: Filter completed todos
        completed_todos = [todo for todo in todos if todo["completed"]]
        incomplete_todos = [todo for todo in todos if not todo["completed"]]
        
        # Verify we have both completed and incomplete todos (typically)
        assert len(todos) > 0
        
        # Verify all todos belong to the user
        for todo in todos:
            assert todo["userId"] == user_id


@pytest.mark.e2e
class TestCRUDWorkflows:
    """Test complete CRUD (Create, Read, Update, Delete) workflows."""
    
    def test_post_crud_workflow(self, api_client, test_post_data):
        """Test complete CRUD workflow for posts."""
        # CREATE
        create_response = api_client.post("/posts", json=test_post_data)
        assert_status_code(create_response, 201)
        
        created_post = create_response.json()
        post_id = created_post["id"]
        
        # Verify creation
        assert created_post["title"] == test_post_data["title"]
        assert created_post["body"] == test_post_data["body"]
        assert "id" in created_post
        
        # READ
        read_response = api_client.get(f"/posts/{post_id}")
        assert_status_code(read_response, 200)
        
        read_post = read_response.json()
        assert read_post["id"] == post_id
        
        # UPDATE
        update_data = {
            **created_post,
            "title": "Updated Title",
            "body": "Updated body content"
        }
        update_response = api_client.put(f"/posts/{post_id}", json=update_data)
        assert_status_code(update_response, 200)
        
        updated_post = update_response.json()
        assert updated_post["title"] == "Updated Title"
        assert updated_post["body"] == "Updated body content"
        
        # PARTIAL UPDATE (PATCH)
        patch_data = {"title": "Patched Title"}
        patch_response = api_client.patch(f"/posts/{post_id}", json=patch_data)
        assert_status_code(patch_response, 200)
        
        patched_post = patch_response.json()
        assert patched_post["title"] == "Patched Title"
        
        # DELETE
        delete_response = api_client.delete(f"/posts/{post_id}")
        assert_status_code(delete_response, 200)
    
    def test_todo_crud_workflow(self, api_client, test_todo_data):
        """Test complete CRUD workflow for todos."""
        # CREATE
        create_response = api_client.post("/todos", json=test_todo_data)
        assert_status_code(create_response, 201)
        
        created_todo = create_response.json()
        todo_id = created_todo["id"]
        
        # Verify creation
        assert created_todo["title"] == test_todo_data["title"]
        assert created_todo["completed"] == test_todo_data["completed"]
        
        # READ
        read_response = api_client.get(f"/todos/{todo_id}")
        assert_status_code(read_response, 200)
        
        # UPDATE - Mark as completed
        update_data = {
            **created_todo,
            "completed": True
        }
        update_response = api_client.put(f"/todos/{todo_id}", json=update_data)
        assert_status_code(update_response, 200)
        
        updated_todo = update_response.json()
        assert updated_todo["completed"] is True
        
        # DELETE
        delete_response = api_client.delete(f"/todos/{todo_id}")
        assert_status_code(delete_response, 200)


@pytest.mark.e2e
class TestDataAggregationWorkflows:
    """Test workflows involving data aggregation."""
    
    def test_aggregate_user_content(self, api_client):
        """Test aggregating all content for a user."""
        user_id = 1
        
        # Get all user content in parallel using threads
        import concurrent.futures
        
        def get_posts():
            return api_client.get(f"/posts", params={"userId": user_id})
        
        def get_todos():
            return api_client.get(f"/todos", params={"userId": user_id})
        
        def get_albums():
            return api_client.get(f"/albums", params={"userId": user_id})
        
        # Execute all requests concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            posts_future = executor.submit(get_posts)
            todos_future = executor.submit(get_todos)
            albums_future = executor.submit(get_albums)
            
            posts_response = posts_future.result()
            todos_response = todos_future.result()
            albums_response = albums_future.result()
        
        # Verify all requests succeeded
        assert_status_code(posts_response, 200)
        assert_status_code(todos_response, 200)
        assert_status_code(albums_response, 200)
        
        # Get the data
        posts = posts_response.json()
        todos = todos_response.json()
        albums = albums_response.json()
        
        # Aggregate stats
        total_content = len(posts) + len(todos) + len(albums)
        completed_todos = len([t for t in todos if t.get("completed", False)])
        
        # Verify we have content
        assert total_content > 0
        assert len(posts) > 0
        
        # Log aggregated data
        print(f"\nUser {user_id} content summary:")
        print(f"  Posts: {len(posts)}")
        print(f"  Todos: {len(todos)} ({completed_todos} completed)")
        print(f"  Albums: {len(albums)}")
        print(f"  Total items: {total_content}")
    
    def test_post_with_all_comments(self, api_client):
        """Test getting a post with all its comments."""
        post_id = 1
        
        # Get post
        post_response = api_client.get(f"/posts/{post_id}")
        assert_status_code(post_response, 200)
        post = post_response.json()
        
        # Get comments for the post
        comments_response = api_client.get(f"/comments", params={"postId": post_id})
        assert_status_code(comments_response, 200)
        comments = comments_response.json()
        
        # Enrich post with comments
        post_with_comments = {
            **post,
            "comments": comments,
            "comment_count": len(comments)
        }
        
        # Verify structure
        assert "comments" in post_with_comments
        assert post_with_comments["comment_count"] == len(comments)
        assert all(c["postId"] == post_id for c in comments)


@pytest.mark.e2e
@pytest.mark.asyncio
class TestAsyncWorkflows:
    """Test async end-to-end workflows."""
    
    async def test_async_crud_workflow(self, async_api_client, test_post_data):
        """Test async CRUD workflow."""
        # CREATE
        create_response = await async_api_client.post_async("/posts", json=test_post_data)
        assert_status_code(create_response, 201)
        created_post = create_response.json()
        post_id = created_post["id"]
        
        # READ
        read_response = await async_api_client.get_async(f"/posts/{post_id}")
        assert_status_code(read_response, 200)
        
        # UPDATE
        update_data = {**created_post, "title": "Async Updated"}
        update_response = await async_api_client.put_async(f"/posts/{post_id}", json=update_data)
        assert_status_code(update_response, 200)
        
        # DELETE
        delete_response = await async_api_client.delete_async(f"/posts/{post_id}")
        assert_status_code(delete_response, 200)
    
    async def test_async_parallel_aggregation(self, async_api_client):
        """Test async parallel data aggregation."""
        import asyncio
        
        user_id = 1
        
        # Create tasks for parallel execution
        posts_task = async_api_client.get_async(f"/posts", params={"userId": user_id})
        todos_task = async_api_client.get_async(f"/todos", params={"userId": user_id})
        albums_task = async_api_client.get_async(f"/albums", params={"userId": user_id})
        
        # Execute all tasks concurrently
        posts_response, todos_response, albums_response = await asyncio.gather(
            posts_task, todos_task, albums_task
        )
        
        # Verify all succeeded
        assert_status_code(posts_response, 200)
        assert_status_code(todos_response, 200)
        assert_status_code(albums_response, 200)
        
        # Verify data
        posts = posts_response.json()
        todos = todos_response.json()
        albums = albums_response.json()
        
        assert_is_list(posts, min_length=1)
        assert_is_list(todos, min_length=1)
