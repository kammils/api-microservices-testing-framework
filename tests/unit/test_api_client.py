"""
Unit Tests for API Client

Tests the APIClient class functionality in isolation.
"""

import pytest
from unittest.mock import Mock, patch
import httpx

from src.api_client import APIClient


@pytest.mark.unit
class TestAPIClientInitialization:
    """Test API client initialization"""

    def test_client_initialization_with_defaults(self):
        """Test client is initialized with default values"""
        client = APIClient(base_url="https://api.example.com")

        assert client.base_url == "https://api.example.com"
        assert client.timeout == 30.0
        assert client.max_retries == 3
        assert client.verify_ssl is True

        client.close()

    def test_client_initialization_with_custom_values(self):
        """Test client is initialized with custom values"""
        headers = {"X-Custom-Header": "value"}
        client = APIClient(
            base_url="https://api.example.com",
            timeout=60.0,
            max_retries=5,
            verify_ssl=False,
            headers=headers,
        )

        assert client.timeout == 60.0
        assert client.max_retries == 5
        assert client.verify_ssl is False
        assert "X-Custom-Header" in client.default_headers

        client.close()

    def test_base_url_normalization(self):
        """Test base URL is normalized (trailing slash removed)"""
        client = APIClient(base_url="https://api.example.com/")
        assert client.base_url == "https://api.example.com"
        client.close()


@pytest.mark.unit
class TestAPIClientHeaders:
    """Test API client header management"""

    def test_set_auth_header(self):
        """Test setting authentication header"""
        client = APIClient(base_url="https://api.example.com")
        client.set_auth_header("Bearer", "test-token-123")

        assert client.default_headers["Authorization"] == "Bearer test-token-123"
        client.close()

    def test_set_custom_header(self):
        """Test setting custom header"""
        client = APIClient(base_url="https://api.example.com")
        client.set_header("X-API-Key", "my-api-key")

        assert client.default_headers["X-API-Key"] == "my-api-key"
        client.close()

    def test_remove_header(self):
        """Test removing header"""
        client = APIClient(base_url="https://api.example.com")
        client.set_header("X-Custom", "value")
        assert "X-Custom" in client.default_headers

        client.remove_header("X-Custom")
        assert "X-Custom" not in client.default_headers

        client.close()


@pytest.mark.unit
class TestAPIClientURLBuilding:
    """Test URL building functionality"""

    def test_build_url_with_simple_endpoint(self):
        """Test building URL with simple endpoint"""
        client = APIClient(base_url="https://api.example.com")
        url = client._build_url("/users")

        assert url == "https://api.example.com/users"
        client.close()

    def test_build_url_without_leading_slash(self):
        """Test building URL when endpoint doesn't start with /"""
        client = APIClient(base_url="https://api.example.com")
        url = client._build_url("users")

        assert url == "https://api.example.com/users"
        client.close()

    def test_build_url_with_nested_endpoint(self):
        """Test building URL with nested endpoint"""
        client = APIClient(base_url="https://api.example.com")
        url = client._build_url("/users/123/orders")

        assert url == "https://api.example.com/users/123/orders"
        client.close()

    def test_build_url_with_full_url(self):
        """Test building URL when endpoint is already a full URL"""
        client = APIClient(base_url="https://api.example.com")
        url = client._build_url("https://other-api.example.com/resource")

        assert url == "https://other-api.example.com/resource"
        client.close()


@pytest.mark.unit
class TestAPIClientDataMasking:
    """Test sensitive data masking"""

    def test_mask_sensitive_headers(self):
        """Test masking sensitive headers"""
        headers = {
            "Authorization": "Bearer secret-token",
            "X-API-Key": "my-secret-key",
            "Content-Type": "application/json",
        }

        masked = APIClient._mask_sensitive_headers(headers)

        assert masked["Authorization"] == "***MASKED***"
        assert masked["X-API-Key"] == "***MASKED***"
        assert masked["Content-Type"] == "application/json"

    def test_mask_sensitive_data(self):
        """Test masking sensitive data fields"""
        data = {
            "username": "testuser",
            "password": "secret123",
            "api_key": "key123",
            "email": "test@example.com",
        }

        masked = APIClient._mask_sensitive_data(data)

        assert masked["username"] == "testuser"
        assert masked["password"] == "***MASKED***"
        assert masked["api_key"] == "***MASKED***"
        assert masked["email"] == "test@example.com"


@pytest.mark.unit
class TestAPIClientContextManager:
    """Test context manager functionality"""

    def test_context_manager_sync(self):
        """Test using client as sync context manager"""
        with APIClient(base_url="https://api.example.com") as client:
            assert client is not None
            assert client.base_url == "https://api.example.com"
        # Client should be closed after context

    @pytest.mark.asyncio
    async def test_context_manager_async(self):
        """Test using client as async context manager"""
        async with APIClient(base_url="https://api.example.com") as client:
            assert client is not None
            assert client.base_url == "https://api.example.com"
        # Client should be closed after context


@pytest.mark.unit
class TestAPIClientMocking:
    """Test API client with mocked requests"""

    @patch("httpx.Client.request")
    def test_get_request(self, mock_request):
        """Test GET request is made correctly"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "name": "Test"}
        mock_response.reason_phrase = "OK"
        mock_response.elapsed.total_seconds.return_value = 0.5
        mock_response.text = '{"id": 1, "name": "Test"}'
        mock_response.headers = {}

        mock_request.return_value = mock_response

        client = APIClient(base_url="https://api.example.com")
        response = client.get("/users/1")

        assert response.status_code == 200
        mock_request.assert_called_once()

        client.close()

    @patch("httpx.Client.request")
    def test_post_request(self, mock_request):
        """Test POST request is made correctly"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 1, "created": True}
        mock_response.reason_phrase = "Created"
        mock_response.elapsed.total_seconds.return_value = 0.7
        mock_response.text = '{"id": 1, "created": True}'
        mock_response.headers = {}

        mock_request.return_value = mock_response

        client = APIClient(base_url="https://api.example.com")
        response = client.post("/users", json={"name": "Test User"})

        assert response.status_code == 201
        mock_request.assert_called_once()

        client.close()
