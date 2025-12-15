"""
Custom Assertion Helpers

Provides custom assertion functions for API testing with detailed error messages.
"""

from typing import Any, Dict, Optional, Union
import httpx


def assert_status_code(response: httpx.Response, expected: int, message: Optional[str] = None):
    """
    Assert response status code matches expected value.

    Args:
        response: HTTP response object
        expected: Expected status code
        message: Optional custom error message
    """
    actual = response.status_code
    error_msg = message or (
        f"Expected status code {expected}, but got {actual}.\n"
        f"Response: {response.text[:200]}"
    )
    assert actual == expected, error_msg


def assert_status_code_in(
    response: httpx.Response, expected_codes: list[int], message: Optional[str] = None
):
    """
    Assert response status code is in expected list.

    Args:
        response: HTTP response object
        expected_codes: List of expected status codes
        message: Optional custom error message
    """
    actual = response.status_code
    error_msg = message or (
        f"Expected status code to be one of {expected_codes}, but got {actual}.\n"
        f"Response: {response.text[:200]}"
    )
    assert actual in expected_codes, error_msg


def assert_response_time(response: httpx.Response, max_time: float, message: Optional[str] = None):
    """
    Assert response time is within acceptable limit.

    Args:
        response: HTTP response object
        max_time: Maximum acceptable response time in seconds
        message: Optional custom error message
    """
    actual_time = response.elapsed.total_seconds()
    error_msg = message or f"Response time {actual_time:.2f}s exceeded maximum {max_time}s"
    assert actual_time <= max_time, error_msg


def assert_json_response(response: httpx.Response, message: Optional[str] = None):
    """
    Assert response is valid JSON.

    Args:
        response: HTTP response object
        message: Optional custom error message
    """
    try:
        response.json()
    except Exception as e:
        error_msg = message or f"Response is not valid JSON: {str(e)}\nResponse: {response.text}"
        raise AssertionError(error_msg)


def assert_json_contains(
    response: httpx.Response, expected_data: Dict[str, Any], message: Optional[str] = None
):
    """
    Assert response JSON contains expected key-value pairs.

    Args:
        response: HTTP response object
        expected_data: Dictionary of expected key-value pairs
        message: Optional custom error message
    """
    actual_data = response.json()

    for key, expected_value in expected_data.items():
        if key not in actual_data:
            error_msg = message or f"Key '{key}' not found in response.\nResponse: {actual_data}"
            raise AssertionError(error_msg)

        if actual_data[key] != expected_value:
            error_msg = message or (
                f"Key '{key}': expected '{expected_value}', got '{actual_data[key]}'"
            )
            raise AssertionError(error_msg)


def assert_json_has_keys(
    response: httpx.Response, expected_keys: list[str], message: Optional[str] = None
):
    """
    Assert response JSON has all expected keys.

    Args:
        response: HTTP response object
        expected_keys: List of expected keys
        message: Optional custom error message
    """
    actual_data = response.json()
    missing_keys = [key for key in expected_keys if key not in actual_data]

    if missing_keys:
        error_msg = message or (
            f"Missing keys in response: {missing_keys}\nResponse: {actual_data}"
        )
        raise AssertionError(error_msg)


def assert_json_schema(
    data: Dict[str, Any],
    schema: Dict[str, type],
    strict: bool = False,
    message: Optional[str] = None,
):
    """
    Assert data matches expected schema (field types).

    Args:
        data: Data to validate
        schema: Dictionary mapping field names to expected types
        strict: If True, data must not have extra fields
        message: Optional custom error message
    """
    # Check required fields
    for field, expected_type in schema.items():
        if field not in data:
            error_msg = message or f"Required field '{field}' not found in data"
            raise AssertionError(error_msg)

        actual_type = type(data[field])
        if not isinstance(data[field], expected_type):
            error_msg = message or (
                f"Field '{field}': expected type {expected_type.__name__}, "
                f"got {actual_type.__name__}"
            )
            raise AssertionError(error_msg)

    # Check for extra fields in strict mode
    if strict:
        extra_fields = set(data.keys()) - set(schema.keys())
        if extra_fields:
            error_msg = message or f"Unexpected fields in data: {extra_fields}"
            raise AssertionError(error_msg)


def assert_header_present(
    response: httpx.Response, header_name: str, message: Optional[str] = None
):
    """
    Assert response contains specified header.

    Args:
        response: HTTP response object
        header_name: Name of expected header
        message: Optional custom error message
    """
    if header_name not in response.headers:
        error_msg = message or (
            f"Header '{header_name}' not found in response.\n"
            f"Available headers: {list(response.headers.keys())}"
        )
        raise AssertionError(error_msg)


def assert_header_value(
    response: httpx.Response,
    header_name: str,
    expected_value: str,
    message: Optional[str] = None,
):
    """
    Assert response header has expected value.

    Args:
        response: HTTP response object
        header_name: Name of header
        expected_value: Expected header value
        message: Optional custom error message
    """
    assert_header_present(response, header_name)

    actual_value = response.headers[header_name]
    if actual_value != expected_value:
        error_msg = message or (
            f"Header '{header_name}': expected '{expected_value}', got '{actual_value}'"
        )
        raise AssertionError(error_msg)


def assert_content_type(
    response: httpx.Response, expected_type: str, message: Optional[str] = None
):
    """
    Assert response content type matches expected.

    Args:
        response: HTTP response object
        expected_type: Expected content type (e.g., 'application/json')
        message: Optional custom error message
    """
    content_type = response.headers.get("content-type", "")
    if expected_type not in content_type:
        error_msg = message or (
            f"Expected content type '{expected_type}', got '{content_type}'"
        )
        raise AssertionError(error_msg)


def assert_list_length(
    items: list, expected_length: int, operator: str = "==", message: Optional[str] = None
):
    """
    Assert list length matches condition.

    Args:
        items: List to check
        expected_length: Expected length
        operator: Comparison operator ('==', '>', '<', '>=', '<=')
        message: Optional custom error message
    """
    actual_length = len(items)

    operators = {
        "==": lambda a, b: a == b,
        ">": lambda a, b: a > b,
        "<": lambda a, b: a < b,
        ">=": lambda a, b: a >= b,
        "<=": lambda a, b: a <= b,
    }

    if operator not in operators:
        raise ValueError(f"Invalid operator: {operator}")

    if not operators[operator](actual_length, expected_length):
        error_msg = message or (
            f"Expected list length {operator} {expected_length}, got {actual_length}"
        )
        raise AssertionError(error_msg)


def assert_success_response(response: httpx.Response, message: Optional[str] = None):
    """
    Assert response is successful (status code 2xx).

    Args:
        response: HTTP response object
        message: Optional custom error message
    """
    if not (200 <= response.status_code < 300):
        error_msg = message or (
            f"Expected successful response (2xx), got {response.status_code}.\n"
            f"Response: {response.text[:200]}"
        )
        raise AssertionError(error_msg)


def assert_error_response(
    response: httpx.Response, expected_error: Optional[str] = None, message: Optional[str] = None
):
    """
    Assert response is an error (status code 4xx or 5xx).

    Args:
        response: HTTP response object
        expected_error: Optional expected error message substring
        message: Optional custom error message
    """
    if 200 <= response.status_code < 300:
        error_msg = message or f"Expected error response, got successful status {response.status_code}"
        raise AssertionError(error_msg)

    if expected_error:
        response_text = response.text
        if expected_error not in response_text:
            error_msg = message or (
                f"Expected error message containing '{expected_error}', "
                f"got: {response_text[:200]}"
            )
            raise AssertionError(error_msg)
