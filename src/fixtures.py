"""
Pytest Fixtures Module

Provides reusable fixtures for testing API and microservices.
"""

import logging
from typing import Generator

import pytest

from src.api_client import APIClient
from src.config import get_config

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def config():
    """Provide test configuration"""
    return get_config()


@pytest.fixture(scope="session")
def base_url(config):
    """Provide base URL from configuration"""
    return config.api_base_url


@pytest.fixture(scope="function")
def api_client(config) -> Generator[APIClient, None, None]:
    """
    Provide API client instance.
    Function-scoped to ensure clean state for each test.
    """
    client = APIClient(
        base_url=config.api_base_url,
        timeout=config.api_timeout,
        max_retries=config.api_max_retries,
        verify_ssl=config.api_verify_ssl,
    )

    # Set authentication if available
    if config.auth_token:
        client.set_auth_header("Bearer", config.auth_token)
    elif config.api_key:
        client.set_header("X-API-Key", config.api_key)

    yield client

    # Cleanup
    client.close()


@pytest.fixture(scope="function")
def authenticated_client(config) -> Generator[APIClient, None, None]:
    """
    Provide authenticated API client.
    Requires AUTH_TOKEN or API_KEY in environment.
    """
    client = APIClient(
        base_url=config.api_base_url,
        timeout=config.api_timeout,
        max_retries=config.api_max_retries,
        verify_ssl=config.api_verify_ssl,
    )

    # Set authentication
    if config.auth_token:
        client.set_auth_header("Bearer", config.auth_token)
        logger.info("Client authenticated with Bearer token")
    elif config.api_key:
        client.set_header("X-API-Key", config.api_key)
        logger.info("Client authenticated with API key")
    else:
        pytest.skip("No authentication credentials available")

    yield client

    # Cleanup
    client.close()


@pytest.fixture(scope="function")
def user_service_client(config) -> Generator[APIClient, None, None]:
    """Provide API client for User Service"""
    client = APIClient(
        base_url=config.user_service_url,
        timeout=config.api_timeout,
        max_retries=config.api_max_retries,
        verify_ssl=config.api_verify_ssl,
    )
    yield client
    client.close()


@pytest.fixture(scope="function")
def order_service_client(config) -> Generator[APIClient, None, None]:
    """Provide API client for Order Service"""
    client = APIClient(
        base_url=config.order_service_url,
        timeout=config.api_timeout,
        max_retries=config.api_max_retries,
        verify_ssl=config.api_verify_ssl,
    )
    yield client
    client.close()


@pytest.fixture(scope="function")
def product_service_client(config) -> Generator[APIClient, None, None]:
    """Provide API client for Product Service"""
    client = APIClient(
        base_url=config.product_service_url,
        timeout=config.api_timeout,
        max_retries=config.api_max_retries,
        verify_ssl=config.api_verify_ssl,
    )
    yield client
    client.close()


@pytest.fixture(autouse=True)
def log_test_info(request):
    """Automatically log test execution info for all tests"""
    logger.info("=" * 80)
    logger.info(f"Starting test: {request.node.nodeid}")
    logger.info("=" * 80)

    yield

    logger.info("=" * 80)
    logger.info(f"Completed test: {request.node.nodeid}")
    logger.info("=" * 80)


@pytest.fixture(scope="function")
def sample_test_data():
    """Provide sample test data"""
    return {
        "user": {
            "name": "Test User",
            "email": "test@example.com",
            "age": 30,
        },
        "product": {
            "name": "Test Product",
            "price": 99.99,
            "category": "Electronics",
        },
        "order": {
            "product_id": 1,
            "quantity": 2,
            "total": 199.98,
        },
    }
