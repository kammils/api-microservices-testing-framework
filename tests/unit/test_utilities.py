"""
Unit Tests for Utilities

Tests for utility functions, helpers, and decorators.
"""

import pytest
import time
from src.utils.logger import get_logger, StructuredLogger
from src.utils.decorators import (
    log_execution_time,
    retry_on_exception,
    timeout,
)
from src.validators.schema_validator import SchemaValidator
from src.fixtures.factories import (
    UserFactory,
    PostFactory,
    generate_users,
    generate_posts,
)


@pytest.mark.unit
class TestLogger:
    """Test logger functionality."""
    
    def test_logger_creation(self):
        """Test creating a logger instance."""
        logger = get_logger("test_logger")
        
        assert isinstance(logger, StructuredLogger)
        assert logger.logger.name == "test_logger"
    
    def test_logger_info_message(self, test_logger):
        """Test logging info message."""
        # Should not raise exception
        test_logger.info("Test info message")
        test_logger.info("Test with context", context={"key": "value"})
    
    def test_logger_error_message(self, test_logger):
        """Test logging error message."""
        test_logger.error("Test error message")
        test_logger.error("Test error with context", context={"error": "details"})
    
    def test_logger_request_logging(self, test_logger):
        """Test request logging."""
        test_logger.log_request(
            method="GET",
            url="https://api.example.com/endpoint",
            status_code=200,
            response_time=0.5
        )


@pytest.mark.unit
class TestDecorators:
    """Test decorator functionality."""
    
    def test_log_execution_time_decorator(self):
        """Test log_execution_time decorator."""
        
        @log_execution_time
        def sample_function():
            time.sleep(0.1)
            return "result"
        
        result = sample_function()
        assert result == "result"
    
    def test_retry_decorator_success(self):
        """Test retry decorator with successful execution."""
        
        @retry_on_exception(max_attempts=3)
        def successful_function():
            return "success"
        
        result = successful_function()
        assert result == "success"
    
    def test_retry_decorator_eventual_success(self):
        """Test retry decorator with eventual success."""
        attempts = {"count": 0}
        
        @retry_on_exception(max_attempts=3, wait_min=0.1, wait_max=0.2)
        def eventually_successful():
            attempts["count"] += 1
            if attempts["count"] < 2:
                raise ValueError("Temporary failure")
            return "success"
        
        result = eventually_successful()
        assert result == "success"
        assert attempts["count"] == 2
    
    def test_timeout_decorator(self):
        """Test timeout decorator."""
        
        @timeout(2)
        def fast_function():
            time.sleep(0.1)
            return "done"
        
        result = fast_function()
        assert result == "done"


@pytest.mark.unit
class TestSchemaValidator:
    """Test schema validator functionality."""
    
    def test_validator_creation(self):
        """Test creating a schema validator."""
        validator = SchemaValidator()
        assert validator is not None
    
    def test_validate_simple_schema(self, schema_validator):
        """Test validating data against a simple schema."""
        data = {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com"
        }
        
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "email": {"type": "string"}
            },
            "required": ["name", "email"]
        }
        
        result = schema_validator.validate(data, schema)
        assert result is True
    
    def test_validate_invalid_data(self, schema_validator):
        """Test validation fails for invalid data."""
        data = {
            "name": "John Doe",
            "age": "thirty"  # Should be integer
        }
        
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name", "age"]
        }
        
        with pytest.raises(Exception):
            schema_validator.validate(data, schema, raise_on_error=True)
    
    def test_create_object_schema(self):
        """Test creating an object schema."""
        schema = SchemaValidator.create_object_schema(
            properties={
                "id": {"type": "integer"},
                "name": {"type": "string"}
            },
            required=["id"]
        )
        
        assert schema["type"] == "object"
        assert "id" in schema["properties"]
        assert "id" in schema["required"]
    
    def test_create_array_schema(self):
        """Test creating an array schema."""
        schema = SchemaValidator.create_array_schema(
            items_schema={"type": "string"},
            min_items=1,
            max_items=10
        )
        
        assert schema["type"] == "array"
        assert schema["minItems"] == 1
        assert schema["maxItems"] == 10
    
    def test_validate_list(self, schema_validator):
        """Test validating a list of items."""
        data_list = [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
        ]
        
        schema = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"}
            },
            "required": ["id", "name"]
        }
        
        result = schema_validator.validate_list(data_list, schema)
        assert result is True


@pytest.mark.unit
class TestFactories:
    """Test Factory Boy factories."""
    
    def test_user_factory(self):
        """Test UserFactory generates valid data."""
        user = UserFactory()
        
        assert "id" in user
        assert "name" in user
        assert "email" in user
        assert "username" in user
        assert "@" in user["email"]
    
    def test_post_factory(self):
        """Test PostFactory generates valid data."""
        post = PostFactory()
        
        assert "id" in post
        assert "userId" in post
        assert "title" in post
        assert "body" in post
    
    def test_generate_multiple_users(self):
        """Test generating multiple users."""
        users = generate_users(count=5)
        
        assert len(users) == 5
        
        # Check unique IDs
        ids = [user["id"] for user in users]
        assert len(set(ids)) == 5
    
    def test_generate_multiple_posts(self):
        """Test generating multiple posts."""
        posts = generate_posts(count=10)
        
        assert len(posts) == 10
        
        # All posts should have required fields
        for post in posts:
            assert "id" in post
            assert "title" in post
            assert "body" in post


@pytest.mark.unit
class TestAssertions:
    """Test custom assertion helpers."""
    
    def test_assert_json_contains(self):
        """Test assert_json_contains helper."""
        from src.utils.assertions import assert_json_contains
        
        data = {"name": "John", "age": 30, "email": "john@example.com"}
        
        # Should pass
        assert_json_contains(data, ["name", "age"])
        
        # Should fail
        with pytest.raises(AssertionError):
            assert_json_contains(data, ["name", "missing_field"])
    
    def test_assert_json_values(self):
        """Test assert_json_values helper."""
        from src.utils.assertions import assert_json_values
        
        data = {"name": "John", "age": 30}
        
        # Should pass
        assert_json_values(data, {"name": "John", "age": 30})
        
        # Should fail
        with pytest.raises(AssertionError):
            assert_json_values(data, {"name": "Jane"})
    
    def test_assert_not_empty(self):
        """Test assert_not_empty helper."""
        from src.utils.assertions import assert_not_empty
        
        # Should pass
        assert_not_empty("text")
        assert_not_empty([1, 2, 3])
        assert_not_empty({"key": "value"})
        
        # Should fail
        with pytest.raises(AssertionError):
            assert_not_empty("")
        
        with pytest.raises(AssertionError):
            assert_not_empty([])
    
    def test_assert_is_list(self):
        """Test assert_is_list helper."""
        from src.utils.assertions import assert_is_list
        
        # Should pass
        assert_is_list([1, 2, 3])
        assert_is_list([1, 2, 3], min_length=2, max_length=5)
        
        # Should fail
        with pytest.raises(AssertionError):
            assert_is_list("not a list")
        
        with pytest.raises(AssertionError):
            assert_is_list([1, 2], min_length=5)
