"""
HTTP Client Wrapper Module

This module provides a robust HTTP client wrapper with built-in retry logic,
request/response logging, and support for various HTTP methods (GET, POST, PUT, PATCH, DELETE).
"""

import logging
import json
import time
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry as URLRetry


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class APIClient:
    """
    A robust HTTP client wrapper with retry logic, logging, and support for multiple HTTP methods.
    
    Features:
    - Automatic retry with exponential backoff
    - Request/response logging
    - Support for GET, POST, PUT, PATCH, DELETE methods
    - Session management with connection pooling
    - Configurable timeouts and headers
    """
    
    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        retry_on_status_codes: Optional[list] = None,
        headers: Optional[Dict[str, str]] = None,
        verify_ssl: bool = True
    ):
        """
        Initialize the API Client.
        
        Args:
            base_url: Base URL for API endpoints
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retry attempts (default: 3)
            backoff_factor: Backoff factor for exponential backoff (default: 0.5)
            retry_on_status_codes: HTTP status codes to retry on (default: [429, 500, 502, 503, 504])
            headers: Additional headers to include in requests
            verify_ssl: Whether to verify SSL certificates (default: True)
        """
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.retry_on_status_codes = retry_on_status_codes or [429, 500, 502, 503, 504]
        self.verify_ssl = verify_ssl
        
        self.session = requests.Session()
        self._setup_session_with_retries()
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'APIClient/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Add custom headers if provided
        if headers:
            self.session.headers.update(headers)
        
        logger.info(f"APIClient initialized with base_url: {base_url}")
    
    def _setup_session_with_retries(self) -> None:
        """Configure the session with automatic retry strategy."""
        retry_strategy = URLRetry(
            total=self.max_retries,
            status_forcelist=self.retry_on_status_codes,
            backoff_factor=self.backoff_factor,
            allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        logger.debug(f"Session configured with retry strategy: max_retries={self.max_retries}")
    
    def _log_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Union[Dict, str]] = None,
        params: Optional[Dict] = None
    ) -> None:
        """Log request details."""
        logger.info(f"REQUEST: {method} {url}")
        if params:
            logger.debug(f"Query Parameters: {params}")
        if headers:
            # Mask sensitive headers
            safe_headers = {
                k: v if k.lower() not in ['authorization', 'x-api-key', 'password']
                else '***MASKED***'
                for k, v in headers.items()
            }
            logger.debug(f"Headers: {safe_headers}")
        if data:
            try:
                if isinstance(data, str):
                    data_to_log = json.loads(data)
                else:
                    data_to_log = data
                # Mask sensitive fields in body
                safe_data = self._mask_sensitive_data(data_to_log)
                logger.debug(f"Body: {json.dumps(safe_data, indent=2)}")
            except (json.JSONDecodeError, TypeError):
                logger.debug(f"Body: {data}")
    
    def _log_response(self, response: requests.Response) -> None:
        """Log response details."""
        logger.info(
            f"RESPONSE: {response.status_code} {response.reason} "
            f"(took {response.elapsed.total_seconds():.2f}s)"
        )
        logger.debug(f"Response Headers: {dict(response.headers)}")
        
        try:
            if response.text:
                response_json = response.json()
                safe_response = self._mask_sensitive_data(response_json)
                logger.debug(f"Response Body: {json.dumps(safe_response, indent=2)}")
        except (json.JSONDecodeError, ValueError):
            if response.text:
                logger.debug(f"Response Body (raw): {response.text[:500]}")
    
    @staticmethod
    def _mask_sensitive_data(data: Any) -> Any:
        """Mask sensitive fields in data."""
        sensitive_fields = {
            'password', 'token', 'access_token', 'refresh_token',
            'api_key', 'secret', 'authorization', 'x-api-key'
        }
        
        if isinstance(data, dict):
            return {
                k: '***MASKED***' if k.lower() in sensitive_fields else v
                for k, v in data.items()
            }
        return data
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from base URL and endpoint."""
        return urljoin(self.base_url, endpoint.lstrip('/'))
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle response and return parsed JSON or raise exception for error status codes.
        
        Args:
            response: Response object from requests library
            
        Returns:
            Dictionary containing parsed response
            
        Raises:
            requests.exceptions.HTTPError: For 4xx and 5xx status codes
        """
        self._log_response(response)
        
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error: {e}")
            raise
        
        try:
            return response.json() if response.text else {}
        except json.JSONDecodeError:
            logger.warning("Response is not valid JSON")
            return {"raw_response": response.text}
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform a GET request.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            headers: Custom headers
            **kwargs: Additional arguments to pass to requests.get()
            
        Returns:
            Parsed JSON response
        """
        url = self._build_url(endpoint)
        request_headers = {**self.session.headers, **(headers or {})}
        
        self._log_request("GET", url, request_headers, params=params)
        
        response = self.session.get(
            url,
            params=params,
            headers=request_headers,
            timeout=self.timeout,
            verify=self.verify_ssl,
            **kwargs
        )
        
        return self._handle_response(response)
    
    def post(
        self,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        json_data: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform a POST request.
        
        Args:
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            headers: Custom headers
            json_data: Whether to send data as JSON (default: True)
            **kwargs: Additional arguments to pass to requests.post()
            
        Returns:
            Parsed JSON response
        """
        url = self._build_url(endpoint)
        request_headers = {**self.session.headers, **(headers or {})}
        
        # Prepare request body
        request_body = None
        if data:
            request_body = json.dumps(data) if json_data and isinstance(data, dict) else data
        
        self._log_request("POST", url, request_headers, request_body, params=params)
        
        response = self.session.post(
            url,
            data=request_body if not json_data else None,
            json=data if json_data and isinstance(data, dict) else None,
            params=params,
            headers=request_headers,
            timeout=self.timeout,
            verify=self.verify_ssl,
            **kwargs
        )
        
        return self._handle_response(response)
    
    def put(
        self,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        json_data: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform a PUT request.
        
        Args:
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            headers: Custom headers
            json_data: Whether to send data as JSON (default: True)
            **kwargs: Additional arguments to pass to requests.put()
            
        Returns:
            Parsed JSON response
        """
        url = self._build_url(endpoint)
        request_headers = {**self.session.headers, **(headers or {})}
        
        # Prepare request body
        request_body = None
        if data:
            request_body = json.dumps(data) if json_data and isinstance(data, dict) else data
        
        self._log_request("PUT", url, request_headers, request_body, params=params)
        
        response = self.session.put(
            url,
            data=request_body if not json_data else None,
            json=data if json_data and isinstance(data, dict) else None,
            params=params,
            headers=request_headers,
            timeout=self.timeout,
            verify=self.verify_ssl,
            **kwargs
        )
        
        return self._handle_response(response)
    
    def patch(
        self,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        json_data: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform a PATCH request.
        
        Args:
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            headers: Custom headers
            json_data: Whether to send data as JSON (default: True)
            **kwargs: Additional arguments to pass to requests.patch()
            
        Returns:
            Parsed JSON response
        """
        url = self._build_url(endpoint)
        request_headers = {**self.session.headers, **(headers or {})}
        
        # Prepare request body
        request_body = None
        if data:
            request_body = json.dumps(data) if json_data and isinstance(data, dict) else data
        
        self._log_request("PATCH", url, request_headers, request_body, params=params)
        
        response = self.session.patch(
            url,
            data=request_body if not json_data else None,
            json=data if json_data and isinstance(data, dict) else None,
            params=params,
            headers=request_headers,
            timeout=self.timeout,
            verify=self.verify_ssl,
            **kwargs
        )
        
        return self._handle_response(response)
    
    def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform a DELETE request.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            headers: Custom headers
            **kwargs: Additional arguments to pass to requests.delete()
            
        Returns:
            Parsed JSON response or empty dict if no response body
        """
        url = self._build_url(endpoint)
        request_headers = {**self.session.headers, **(headers or {})}
        
        self._log_request("DELETE", url, request_headers, params=params)
        
        response = self.session.delete(
            url,
            params=params,
            headers=request_headers,
            timeout=self.timeout,
            verify=self.verify_ssl,
            **kwargs
        )
        
        return self._handle_response(response)
    
    def set_auth_header(self, auth_type: str, token: str) -> None:
        """
        Set authentication header.
        
        Args:
            auth_type: Type of authentication (e.g., 'Bearer', 'Basic')
            token: Authentication token
        """
        self.session.headers['Authorization'] = f"{auth_type} {token}"
        logger.info(f"Authentication header set with type: {auth_type}")
    
    def set_custom_header(self, key: str, value: str) -> None:
        """
        Set a custom header.
        
        Args:
            key: Header key
            value: Header value
        """
        self.session.headers[key] = value
        logger.debug(f"Custom header set: {key}")
    
    def remove_header(self, key: str) -> None:
        """
        Remove a header.
        
        Args:
            key: Header key to remove
        """
        if key in self.session.headers:
            del self.session.headers[key]
            logger.debug(f"Header removed: {key}")
    
    def close(self) -> None:
        """Close the session and clean up resources."""
        self.session.close()
        logger.info("APIClient session closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
