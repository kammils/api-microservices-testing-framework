"""
Pytest Fixtures

Provides shared pytest fixtures for API client, logger, and test data.
"""

import pytest
from src.clients.api_client import APIClient
from src.config.settings import settings
from src.utils.logger import get_logger
from src.validators.schema_validator import SchemaValidator

logger = get_logger(__name__)


@pytest.fixture(scope="session")
def api_base_url():
    """Provide API base URL from settings."""
    return settings.api_base_url


@pytest.fixture(scope="session")
def api_timeout():
    """Provide API timeout from settings."""
    return settings.api_timeout


@pytest.fixture
def api_client(api_base_url, api_timeout):
    """
    Provide API client instance.
    
    Creates a new API client for each test with proper cleanup.
    """
    client = APIClient(base_url=api_base_url, timeout=api_timeout)
    yield client
    client.close()


@pytest.fixture(scope="session")
def session_api_client(api_base_url, api_timeout):
    """
    Provide session-scoped API client.
    
    Reuses the same client across all tests in the session.
    Use for tests that don't modify client state.
    """
    client = APIClient(base_url=api_base_url, timeout=api_timeout)
    yield client
    client.close()


@pytest.fixture
async def async_api_client(api_base_url, api_timeout):
    """
    Provide async API client instance.
    
    Creates a new async API client for each async test with proper cleanup.
    """
    async with APIClient(base_url=api_base_url, timeout=api_timeout) as client:
        yield client


@pytest.fixture
def test_logger():
    """Provide logger instance for tests."""
    return get_logger("test")


@pytest.fixture
def schema_validator():
    """Provide schema validator instance."""
    return SchemaValidator()


@pytest.fixture(autouse=True)
def log_test_execution(request):
    """
    Auto-used fixture to log test execution start and end.
    
    Automatically logs the start and completion of each test.
    """
    test_name = request.node.name
    logger.info(f"Starting test: {test_name}")
    
    yield
    
    logger.info(f"Completed test: {test_name}")


@pytest.fixture
def test_user_data():
    """Provide sample test user data."""
    return {
        "name": "Test User",
        "username": "testuser",
        "email": "testuser@example.com",
        "phone": "555-1234",
        "website": "testuser.com"
    }


@pytest.fixture
def test_post_data():
    """Provide sample test post data."""
    return {
        "title": "Test Post Title",
        "body": "This is a test post body with some content.",
        "userId": 1
    }


@pytest.fixture
def test_comment_data():
    """Provide sample test comment data."""
    return {
        "name": "Test Comment",
        "email": "comment@example.com",
        "body": "This is a test comment.",
        "postId": 1
    }


@pytest.fixture
def test_todo_data():
    """Provide sample test todo data."""
    return {
        "title": "Test Todo Item",
        "completed": False,
        "userId": 1
    }
