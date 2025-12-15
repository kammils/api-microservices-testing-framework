"""
Modern API Client Module using Httpx

Provides an async-capable HTTP client with retry logic, timeout handling,
and comprehensive session management for microservices testing.
"""

import logging
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import httpx
from httpx import Response

logger = logging.getLogger(__name__)


class APIClient:
    """
    Modern HTTP client using Httpx with async support, retry logic, and comprehensive features.

    Features:
    - Async and sync support
    - Automatic retry with exponential backoff
    - Request/response logging
    - Support for all HTTP methods
    - Session management with connection pooling
    - Configurable timeouts and headers
    - SSL verification control
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        verify_ssl: bool = True,
        headers: Optional[Dict[str, str]] = None,
        follow_redirects: bool = True,
    ):
        """
        Initialize the API Client.

        Args:
            base_url: Base URL for API endpoints
            timeout: Request timeout in seconds (default: 30.0)
            max_retries: Maximum number of retry attempts (default: 3)
            verify_ssl: Whether to verify SSL certificates (default: True)
            headers: Additional headers to include in requests
            follow_redirects: Whether to follow redirects (default: True)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.verify_ssl = verify_ssl
        self.follow_redirects = follow_redirects

        # Default headers
        default_headers = {
            "User-Agent": "APITestClient/2.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        # Merge with custom headers
        self.default_headers = {**default_headers, **(headers or {})}

        # Create transport with retry logic
        self.transport = httpx.HTTPTransport(retries=max_retries)

        # Create sync client
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            verify=self.verify_ssl,
            follow_redirects=self.follow_redirects,
            headers=self.default_headers,
            transport=self.transport,
        )

        # Create async client (lazy initialization)
        self._async_client: Optional[httpx.AsyncClient] = None

        logger.info(f"APIClient initialized with base_url: {base_url}")

    @property
    def async_client(self) -> httpx.AsyncClient:
        """Get or create async client"""
        if self._async_client is None:
            async_transport = httpx.AsyncHTTPTransport(retries=self.max_retries)
            self._async_client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                verify=self.verify_ssl,
                follow_redirects=self.follow_redirects,
                headers=self.default_headers,
                transport=async_transport,
            )
        return self._async_client

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint"""
        if endpoint.startswith(("http://", "https://")):
            return endpoint
        return urljoin(self.base_url + "/", endpoint.lstrip("/"))

    def _log_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
    ) -> None:
        """Log request details"""
        logger.info(f"REQUEST: {method} {url}")
        if params:
            logger.debug(f"Query Parameters: {params}")
        if headers:
            safe_headers = self._mask_sensitive_headers(headers)
            logger.debug(f"Headers: {safe_headers}")
        if data:
            logger.debug(f"Body: {self._mask_sensitive_data(data)}")

    def _log_response(self, response: Response) -> None:
        """Log response details"""
        logger.info(
            f"RESPONSE: {response.status_code} {response.reason_phrase} "
            f"(took {response.elapsed.total_seconds():.2f}s)"
        )
        logger.debug(f"Response Headers: {dict(response.headers)}")

        if response.text:
            try:
                response_json = response.json()
                safe_response = self._mask_sensitive_data(response_json)
                logger.debug(f"Response Body: {safe_response}")
            except Exception:
                logger.debug(f"Response Body (raw): {response.text[:500]}")

    @staticmethod
    def _mask_sensitive_headers(headers: Dict[str, str]) -> Dict[str, str]:
        """Mask sensitive headers"""
        sensitive_keys = {"authorization", "x-api-key", "api-key", "token", "password"}
        return {k: "***MASKED***" if k.lower() in sensitive_keys else v for k, v in headers.items()}

    @staticmethod
    def _mask_sensitive_data(data: Any) -> Any:
        """Mask sensitive fields in data"""
        if isinstance(data, dict):
            sensitive_fields = {
                "password",
                "token",
                "access_token",
                "refresh_token",
                "api_key",
                "secret",
                "authorization",
            }
            return {
                k: "***MASKED***" if k.lower() in sensitive_fields else v for k, v in data.items()
            }
        return data

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Response:
        """
        Make a generic HTTP request.

        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            json: JSON request body
            headers: Custom headers
            **kwargs: Additional arguments for httpx

        Returns:
            Response object
        """
        url = self._build_url(endpoint)
        request_headers = {**self.default_headers, **(headers or {})}

        self._log_request(method, url, request_headers, params, json or data)

        response = self.client.request(
            method=method,
            url=url,
            params=params,
            data=data,
            json=json,
            headers=request_headers,
            **kwargs,
        )

        self._log_response(response)
        return response

    async def request_async(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Response:
        """
        Make an async HTTP request.

        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            json: JSON request body
            headers: Custom headers
            **kwargs: Additional arguments for httpx

        Returns:
            Response object
        """
        url = self._build_url(endpoint)
        request_headers = {**self.default_headers, **(headers or {})}

        self._log_request(method, url, request_headers, params, json or data)

        response = await self.async_client.request(
            method=method,
            url=url,
            params=params,
            data=data,
            json=json,
            headers=request_headers,
            **kwargs,
        )

        self._log_response(response)
        return response

    # Sync methods
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Response:
        """Make a GET request"""
        return self.request("GET", endpoint, params=params, **kwargs)

    def post(
        self,
        endpoint: str,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        **kwargs,
    ) -> Response:
        """Make a POST request"""
        return self.request("POST", endpoint, data=data, json=json, **kwargs)

    def put(
        self,
        endpoint: str,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        **kwargs,
    ) -> Response:
        """Make a PUT request"""
        return self.request("PUT", endpoint, data=data, json=json, **kwargs)

    def patch(
        self,
        endpoint: str,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        **kwargs,
    ) -> Response:
        """Make a PATCH request"""
        return self.request("PATCH", endpoint, data=data, json=json, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Response:
        """Make a DELETE request"""
        return self.request("DELETE", endpoint, **kwargs)

    # Async methods
    async def get_async(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Response:
        """Make an async GET request"""
        return await self.request_async("GET", endpoint, params=params, **kwargs)

    async def post_async(
        self,
        endpoint: str,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        **kwargs,
    ) -> Response:
        """Make an async POST request"""
        return await self.request_async("POST", endpoint, data=data, json=json, **kwargs)

    async def put_async(
        self,
        endpoint: str,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        **kwargs,
    ) -> Response:
        """Make an async PUT request"""
        return await self.request_async("PUT", endpoint, data=data, json=json, **kwargs)

    async def patch_async(
        self,
        endpoint: str,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        **kwargs,
    ) -> Response:
        """Make an async PATCH request"""
        return await self.request_async("PATCH", endpoint, data=data, json=json, **kwargs)

    async def delete_async(self, endpoint: str, **kwargs) -> Response:
        """Make an async DELETE request"""
        return await self.request_async("DELETE", endpoint, **kwargs)

    def set_auth_header(self, auth_type: str, token: str) -> None:
        """
        Set authentication header.

        Args:
            auth_type: Type of authentication (e.g., 'Bearer', 'Basic')
            token: Authentication token
        """
        auth_value = f"{auth_type} {token}"
        self.default_headers["Authorization"] = auth_value
        self.client.headers["Authorization"] = auth_value
        if self._async_client:
            self._async_client.headers["Authorization"] = auth_value
        logger.info(f"Authentication header set with type: {auth_type}")

    def set_header(self, key: str, value: str) -> None:
        """
        Set a custom header.

        Args:
            key: Header key
            value: Header value
        """
        self.default_headers[key] = value
        self.client.headers[key] = value
        if self._async_client:
            self._async_client.headers[key] = value
        logger.debug(f"Custom header set: {key}")

    def remove_header(self, key: str) -> None:
        """
        Remove a header.

        Args:
            key: Header key to remove
        """
        self.default_headers.pop(key, None)
        self.client.headers.pop(key, None)
        if self._async_client:
            self._async_client.headers.pop(key, None)
        logger.debug(f"Header removed: {key}")

    def close(self) -> None:
        """Close the client and clean up resources"""
        self.client.close()
        if self._async_client:
            # Note: async client should be closed with await in async context
            logger.warning("Async client should be closed in async context with await")
        logger.info("APIClient closed")

    async def close_async(self) -> None:
        """Close the async client"""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None
        logger.info("Async APIClient closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_async()
        self.close()
