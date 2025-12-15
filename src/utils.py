"""
Utility Functions Module

Provides helper functions for testing and data manipulation.
"""

import asyncio
import json
import time
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

import httpx


def retry_on_failure(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator to retry a function on failure.

    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier for delay
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        raise last_exception

        return wrapper

    return decorator


def measure_time(func: Callable) -> Callable:
    """
    Decorator to measure function execution time.

    Args:
        func: Function to measure
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"{func.__name__} took {elapsed:.2f} seconds")
        return result

    return wrapper


async def gather_requests(requests: List[Callable]) -> List[Any]:
    """
    Execute multiple async requests concurrently.

    Args:
        requests: List of async callables

    Returns:
        List of results
    """
    tasks = [req() for req in requests]
    return await asyncio.gather(*tasks)


def load_json_file(filepath: str) -> Dict[str, Any]:
    """
    Load JSON data from file.

    Args:
        filepath: Path to JSON file

    Returns:
        Parsed JSON data
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json_file(filepath: str, data: Dict[str, Any], indent: int = 2) -> None:
    """
    Save data to JSON file.

    Args:
        filepath: Path to save file
        data: Data to save
        indent: JSON indentation
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent)


def parse_response_json(response: httpx.Response) -> Optional[Dict[str, Any]]:
    """
    Safely parse JSON response.

    Args:
        response: HTTP response

    Returns:
        Parsed JSON or None if invalid
    """
    try:
        return response.json()
    except Exception:
        return None


def filter_dict(data: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """
    Filter dictionary to include only specified keys.

    Args:
        data: Source dictionary
        keys: Keys to include

    Returns:
        Filtered dictionary
    """
    return {k: v for k, v in data.items() if k in keys}


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries.

    Args:
        *dicts: Dictionaries to merge

    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        result.update(d)
    return result


def generate_timestamp() -> str:
    """
    Generate ISO format timestamp.

    Returns:
        ISO format timestamp string
    """
    return datetime.now().isoformat()


def generate_unique_id(prefix: str = "") -> str:
    """
    Generate unique ID with optional prefix.

    Args:
        prefix: Optional prefix for ID

    Returns:
        Unique ID string
    """
    timestamp = int(time.time() * 1000)
    return f"{prefix}{timestamp}" if prefix else str(timestamp)


def wait_for_condition(
    condition: Callable[[], bool],
    timeout: float = 10.0,
    interval: float = 0.5,
    error_message: str = "Condition not met within timeout",
) -> None:
    """
    Wait for a condition to be true.

    Args:
        condition: Callable that returns boolean
        timeout: Maximum time to wait in seconds
        interval: Check interval in seconds
        error_message: Error message if timeout

    Raises:
        TimeoutError: If condition not met within timeout
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition():
            return
        time.sleep(interval)

    raise TimeoutError(error_message)


def format_json(data: Any, indent: int = 2) -> str:
    """
    Format data as pretty-printed JSON.

    Args:
        data: Data to format
        indent: Indentation spaces

    Returns:
        Formatted JSON string
    """
    return json.dumps(data, indent=indent, default=str)


def extract_field(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """
    Extract nested field from dictionary using dot notation.

    Args:
        data: Source dictionary
        path: Dot-separated path (e.g., "user.address.city")
        default: Default value if path not found

    Returns:
        Field value or default
    """
    keys = path.split(".")
    current = data

    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default

    return current


def validate_response_schema(
    response: httpx.Response, required_fields: List[str]
) -> tuple[bool, List[str]]:
    """
    Validate response has required fields.

    Args:
        response: HTTP response
        required_fields: List of required field names

    Returns:
        Tuple of (is_valid, missing_fields)
    """
    try:
        data = response.json()
        missing = [field for field in required_fields if field not in data]
        return len(missing) == 0, missing
    except Exception:
        return False, required_fields


def batch_requests(
    client: Any, method: str, endpoints: List[str], **kwargs
) -> List[httpx.Response]:
    """
    Execute batch of requests to multiple endpoints.

    Args:
        client: API client instance
        method: HTTP method
        endpoints: List of endpoints
        **kwargs: Additional request parameters

    Returns:
        List of responses
    """
    responses = []
    for endpoint in endpoints:
        response = client.request(method, endpoint, **kwargs)
        responses.append(response)
    return responses


def calculate_success_rate(responses: List[httpx.Response]) -> float:
    """
    Calculate success rate from list of responses.

    Args:
        responses: List of HTTP responses

    Returns:
        Success rate as percentage (0-100)
    """
    if not responses:
        return 0.0

    successful = sum(1 for r in responses if 200 <= r.status_code < 300)
    return (successful / len(responses)) * 100


def create_pagination_params(page: int = 1, limit: int = 10) -> Dict[str, Any]:
    """
    Create pagination parameters.

    Args:
        page: Page number (1-indexed)
        limit: Items per page

    Returns:
        Pagination parameters dictionary
    """
    return {"page": page, "limit": limit, "offset": (page - 1) * limit}
