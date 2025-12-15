"""
Modern API Client Module

httpx-based async-capable HTTP client with retry logic, timeout handling,
and comprehensive logging.
"""

from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from src.config.settings import settings
from src.config.constants import (
    DEFAULT_HEADERS,
    RETRY_STATUS_CODES,
    DEFAULT_TIMEOUT,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class APIClient:
    """
    Modern httpx-based API client with async support.
    
    Features:
    - Synchronous and asynchronous HTTP methods
    - Automatic retry with exponential backoff
    - Request/response logging
    - Session management
    - Configurable timeouts and headers
    - SSL verification control
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None,
        verify_ssl: Optional[bool] = None,
    ):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL for API endpoints
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Backoff factor for exponential retry
            headers: Custom headers
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = base_url or settings.api_base_url
        self.timeout = timeout or settings.api_timeout
        self.max_retries = max_retries or settings.api_max_retries
        self.backoff_factor = backoff_factor or settings.api_backoff_factor
        self.verify_ssl = verify_ssl if verify_ssl is not None else settings.verify_ssl
        
        # Default headers
        self.headers = DEFAULT_HEADERS.copy()
        if headers:
            self.headers.update(headers)
        
        # Create synchronous client
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self.headers,
            verify=self.verify_ssl,
        )
        
        # Async client (created on demand)
        self._async_client: Optional[httpx.AsyncClient] = None
        
        logger.info(f"APIClient initialized with base_url: {self.base_url}")
    
    def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create async client."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=self.headers,
                verify=self.verify_ssl,
            )
        return self._async_client
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        if endpoint.startswith(("http://", "https://")):
            return endpoint
        return urljoin(self.base_url, endpoint.lstrip("/"))
    
    def _log_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log request details."""
        logger.info(f"REQUEST: {method} {url}")
        if params:
            logger.debug(f"Query params: {params}")
        if headers:
            safe_headers = self._mask_sensitive_headers(headers)
            logger.debug(f"Headers: {safe_headers}")
    
    def _log_response(self, response: httpx.Response) -> None:
        """Log response details."""
        elapsed_ms = response.elapsed.total_seconds() * 1000
        logger.info(
            f"RESPONSE: {response.status_code} (took {elapsed_ms:.2f}ms)",
            context={
                "status_code": response.status_code,
                "response_time_ms": f"{elapsed_ms:.2f}"
            }
        )
        
        # Log response body (truncated)
        if response.text:
            body_preview = response.text[:500]
            logger.debug(f"Response body: {body_preview}")
    
    @staticmethod
    def _mask_sensitive_headers(headers: Dict[str, str]) -> Dict[str, str]:
        """Mask sensitive header values."""
        sensitive_keys = {"authorization", "x-api-key", "api-key", "token"}
        return {
            k: "***MASKED***" if k.lower() in sensitive_keys else v
            for k, v in headers.items()
        }
    
    def _should_retry(self, response: httpx.Response) -> bool:
        """Check if request should be retried based on status code."""
        return response.status_code in RETRY_STATUS_CODES
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.TransportError, httpx.TimeoutException)),
        reraise=True,
    )
    def _request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """Execute request with retry logic."""
        return self.client.request(method, url, **kwargs)
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """
        Perform synchronous GET request.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            headers: Custom headers
            **kwargs: Additional arguments for httpx
            
        Returns:
            httpx Response object
        """
        url = self._build_url(endpoint)
        request_headers = {**self.headers, **(headers or {})}
        
        self._log_request("GET", url, request_headers, params)
        
        response = self._request_with_retry(
            "GET",
            url,
            params=params,
            headers=request_headers,
            **kwargs
        )
        
        self._log_response(response)
        return response
    
    def post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """
        Perform synchronous POST request.
        
        Args:
            endpoint: API endpoint path
            json: JSON data to send
            data: Form data to send
            params: Query parameters
            headers: Custom headers
            **kwargs: Additional arguments for httpx
            
        Returns:
            httpx Response object
        """
        url = self._build_url(endpoint)
        request_headers = {**self.headers, **(headers or {})}
        
        self._log_request("POST", url, request_headers, params)
        
        response = self._request_with_retry(
            "POST",
            url,
            json=json,
            data=data,
            params=params,
            headers=request_headers,
            **kwargs
        )
        
        self._log_response(response)
        return response
    
    def put(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """
        Perform synchronous PUT request.
        
        Args:
            endpoint: API endpoint path
            json: JSON data to send
            data: Form data to send
            params: Query parameters
            headers: Custom headers
            **kwargs: Additional arguments for httpx
            
        Returns:
            httpx Response object
        """
        url = self._build_url(endpoint)
        request_headers = {**self.headers, **(headers or {})}
        
        self._log_request("PUT", url, request_headers, params)
        
        response = self._request_with_retry(
            "PUT",
            url,
            json=json,
            data=data,
            params=params,
            headers=request_headers,
            **kwargs
        )
        
        self._log_response(response)
        return response
    
    def patch(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """
        Perform synchronous PATCH request.
        
        Args:
            endpoint: API endpoint path
            json: JSON data to send
            data: Form data to send
            params: Query parameters
            headers: Custom headers
            **kwargs: Additional arguments for httpx
            
        Returns:
            httpx Response object
        """
        url = self._build_url(endpoint)
        request_headers = {**self.headers, **(headers or {})}
        
        self._log_request("PATCH", url, request_headers, params)
        
        response = self._request_with_retry(
            "PATCH",
            url,
            json=json,
            data=data,
            params=params,
            headers=request_headers,
            **kwargs
        )
        
        self._log_response(response)
        return response
    
    def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """
        Perform synchronous DELETE request.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            headers: Custom headers
            **kwargs: Additional arguments for httpx
            
        Returns:
            httpx Response object
        """
        url = self._build_url(endpoint)
        request_headers = {**self.headers, **(headers or {})}
        
        self._log_request("DELETE", url, request_headers, params)
        
        response = self._request_with_retry(
            "DELETE",
            url,
            params=params,
            headers=request_headers,
            **kwargs
        )
        
        self._log_response(response)
        return response
    
    # Async methods
    
    async def get_async(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """Perform asynchronous GET request."""
        url = self._build_url(endpoint)
        request_headers = {**self.headers, **(headers or {})}
        
        self._log_request("GET", url, request_headers, params)
        
        async_client = self._get_async_client()
        response = await async_client.get(
            url,
            params=params,
            headers=request_headers,
            **kwargs
        )
        
        self._log_response(response)
        return response
    
    async def post_async(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """Perform asynchronous POST request."""
        url = self._build_url(endpoint)
        request_headers = {**self.headers, **(headers or {})}
        
        self._log_request("POST", url, request_headers, params)
        
        async_client = self._get_async_client()
        response = await async_client.post(
            url,
            json=json,
            data=data,
            params=params,
            headers=request_headers,
            **kwargs
        )
        
        self._log_response(response)
        return response
    
    async def put_async(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """Perform asynchronous PUT request."""
        url = self._build_url(endpoint)
        request_headers = {**self.headers, **(headers or {})}
        
        self._log_request("PUT", url, request_headers, params)
        
        async_client = self._get_async_client()
        response = await async_client.put(
            url,
            json=json,
            data=data,
            params=params,
            headers=request_headers,
            **kwargs
        )
        
        self._log_response(response)
        return response
    
    async def delete_async(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """Perform asynchronous DELETE request."""
        url = self._build_url(endpoint)
        request_headers = {**self.headers, **(headers or {})}
        
        self._log_request("DELETE", url, request_headers, params)
        
        async_client = self._get_async_client()
        response = await async_client.delete(
            url,
            params=params,
            headers=request_headers,
            **kwargs
        )
        
        self._log_response(response)
        return response
    
    def set_auth_header(self, auth_type: str, token: str) -> None:
        """
        Set authentication header.
        
        Args:
            auth_type: Authentication type (e.g., 'Bearer', 'Basic')
            token: Authentication token
        """
        self.headers["Authorization"] = f"{auth_type} {token}"
        self.client.headers["Authorization"] = f"{auth_type} {token}"
        logger.info(f"Authentication header set: {auth_type}")
    
    def set_header(self, key: str, value: str) -> None:
        """Set custom header."""
        self.headers[key] = value
        self.client.headers[key] = value
    
    def remove_header(self, key: str) -> None:
        """Remove header."""
        self.headers.pop(key, None)
        self.client.headers.pop(key, None)
    
    def close(self) -> None:
        """Close all clients."""
        self.client.close()
        if self._async_client:
            # Note: async client should be closed in async context
            logger.info("Async client needs to be closed in async context")
        logger.info("APIClient closed")
    
    async def close_async(self) -> None:
        """Close async client."""
        if self._async_client:
            await self._async_client.aclose()
        logger.info("Async APIClient closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close_async()
