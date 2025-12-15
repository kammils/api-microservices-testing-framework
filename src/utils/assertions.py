"""
Custom Assertions Module

Provides custom assertion helpers for API testing with detailed error messages.
"""

from typing import Any, Dict, List, Optional, Union
import httpx
from src.config.constants import (
    HTTP_OK,
    HTTP_CREATED,
    HTTP_NO_CONTENT,
    HTTP_BAD_REQUEST,
    HTTP_UNAUTHORIZED,
    HTTP_FORBIDDEN,
    HTTP_NOT_FOUND,
)


def assert_status_code(
    response: httpx.Response,
    expected_status: int,
    message: Optional[str] = None
) -> None:
    """
    Assert response status code matches expected value.
    
    Args:
        response: httpx Response object
        expected_status: Expected status code
        message: Optional custom error message
    
    Raises:
        AssertionError: If status code doesn't match
    """
    actual_status = response.status_code
    error_msg = message or (
        f"Expected status code {expected_status}, got {actual_status}. "
        f"Response: {response.text[:200]}"
    )
    assert actual_status == expected_status, error_msg


def assert_response_time(
    response: httpx.Response,
    max_time_seconds: float,
    message: Optional[str] = None
) -> None:
    """
    Assert response time is below threshold.
    
    Args:
        response: httpx Response object
        max_time_seconds: Maximum acceptable response time in seconds
        message: Optional custom error message
    
    Raises:
        AssertionError: If response time exceeds threshold
    """
    response_time = response.elapsed.total_seconds()
    error_msg = message or (
        f"Response time {response_time:.2f}s exceeded threshold of {max_time_seconds}s"
    )
    assert response_time <= max_time_seconds, error_msg


def assert_json_contains(
    response_json: Dict[str, Any],
    expected_keys: List[str],
    message: Optional[str] = None
) -> None:
    """
    Assert JSON response contains expected keys.
    
    Args:
        response_json: JSON response as dictionary
        expected_keys: List of expected keys
        message: Optional custom error message
    
    Raises:
        AssertionError: If any expected key is missing
    """
    missing_keys = [key for key in expected_keys if key not in response_json]
    error_msg = message or f"Missing keys in response: {missing_keys}"
    assert not missing_keys, error_msg


def assert_json_values(
    response_json: Dict[str, Any],
    expected_values: Dict[str, Any],
    message: Optional[str] = None
) -> None:
    """
    Assert JSON response contains expected key-value pairs.
    
    Args:
        response_json: JSON response as dictionary
        expected_values: Dictionary of expected key-value pairs
        message: Optional custom error message
    
    Raises:
        AssertionError: If any value doesn't match
    """
    mismatches = []
    for key, expected_value in expected_values.items():
        actual_value = response_json.get(key)
        if actual_value != expected_value:
            mismatches.append(
                f"{key}: expected {expected_value}, got {actual_value}"
            )
    
    error_msg = message or f"Value mismatches: {', '.join(mismatches)}"
    assert not mismatches, error_msg


def assert_json_schema(
    response_json: Dict[str, Any],
    schema_keys: List[str],
    message: Optional[str] = None
) -> None:
    """
    Assert JSON response matches expected schema (has all required keys).
    
    Args:
        response_json: JSON response as dictionary
        schema_keys: List of required keys
        message: Optional custom error message
    
    Raises:
        AssertionError: If schema doesn't match
    """
    assert_json_contains(response_json, schema_keys, message)


def assert_not_empty(
    value: Union[str, List, Dict],
    message: Optional[str] = None
) -> None:
    """
    Assert value is not empty.
    
    Args:
        value: Value to check
        message: Optional custom error message
    
    Raises:
        AssertionError: If value is empty
    """
    error_msg = message or f"Expected non-empty value, got: {value}"
    assert value, error_msg


def assert_is_list(
    value: Any,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    message: Optional[str] = None
) -> None:
    """
    Assert value is a list with optional length constraints.
    
    Args:
        value: Value to check
        min_length: Minimum list length
        max_length: Maximum list length
        message: Optional custom error message
    
    Raises:
        AssertionError: If value is not a list or length is invalid
    """
    error_msg = message or f"Expected list, got {type(value).__name__}"
    assert isinstance(value, list), error_msg
    
    if min_length is not None:
        assert len(value) >= min_length, f"List length {len(value)} < minimum {min_length}"
    
    if max_length is not None:
        assert len(value) <= max_length, f"List length {len(value)} > maximum {max_length}"


def assert_header_present(
    response: httpx.Response,
    header_name: str,
    message: Optional[str] = None
) -> None:
    """
    Assert response header is present.
    
    Args:
        response: httpx Response object
        header_name: Header name to check
        message: Optional custom error message
    
    Raises:
        AssertionError: If header is not present
    """
    error_msg = message or f"Header '{header_name}' not found in response"
    assert header_name.lower() in [h.lower() for h in response.headers.keys()], error_msg


def assert_header_value(
    response: httpx.Response,
    header_name: str,
    expected_value: str,
    message: Optional[str] = None
) -> None:
    """
    Assert response header has expected value.
    
    Args:
        response: httpx Response object
        header_name: Header name
        expected_value: Expected header value
        message: Optional custom error message
    
    Raises:
        AssertionError: If header value doesn't match
    """
    actual_value = response.headers.get(header_name)
    error_msg = message or (
        f"Header '{header_name}': expected '{expected_value}', got '{actual_value}'"
    )
    assert actual_value == expected_value, error_msg


def assert_successful_response(response: httpx.Response) -> None:
    """
    Assert response is successful (2xx status code).
    
    Args:
        response: httpx Response object
    
    Raises:
        AssertionError: If response is not successful
    """
    assert 200 <= response.status_code < 300, (
        f"Expected successful response (2xx), got {response.status_code}. "
        f"Response: {response.text[:200]}"
    )


def assert_error_response(response: httpx.Response, expected_status: int) -> None:
    """
    Assert response is an error with expected status code.
    
    Args:
        response: httpx Response object
        expected_status: Expected error status code
    
    Raises:
        AssertionError: If status doesn't match or is not an error
    """
    assert response.status_code == expected_status, (
        f"Expected error status {expected_status}, got {response.status_code}"
    )
    assert response.status_code >= 400, (
        f"Expected error status (4xx or 5xx), got {response.status_code}"
    )
