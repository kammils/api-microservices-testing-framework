"""
Constants Module

Defines test constants, endpoints, and fixed values used across the framework.
"""

from typing import Dict, List

# HTTP Status Codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_ACCEPTED = 202
HTTP_NO_CONTENT = 204
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405
HTTP_CONFLICT = 409
HTTP_UNPROCESSABLE_ENTITY = 422
HTTP_TOO_MANY_REQUESTS = 429
HTTP_INTERNAL_SERVER_ERROR = 500
HTTP_BAD_GATEWAY = 502
HTTP_SERVICE_UNAVAILABLE = 503
HTTP_GATEWAY_TIMEOUT = 504

# Retry Configuration
RETRY_STATUS_CODES: List[int] = [
    HTTP_TOO_MANY_REQUESTS,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_BAD_GATEWAY,
    HTTP_SERVICE_UNAVAILABLE,
    HTTP_GATEWAY_TIMEOUT,
]

# Timeouts (in seconds)
DEFAULT_TIMEOUT = 30
SHORT_TIMEOUT = 10
LONG_TIMEOUT = 60

# Content Types
CONTENT_TYPE_JSON = "application/json"
CONTENT_TYPE_XML = "application/xml"
CONTENT_TYPE_FORM = "application/x-www-form-urlencoded"
CONTENT_TYPE_MULTIPART = "multipart/form-data"

# Headers
HEADER_CONTENT_TYPE = "Content-Type"
HEADER_ACCEPT = "Accept"
HEADER_AUTHORIZATION = "Authorization"
HEADER_USER_AGENT = "User-Agent"
HEADER_API_KEY = "X-API-Key"

# Default Headers
DEFAULT_HEADERS: Dict[str, str] = {
    HEADER_ACCEPT: CONTENT_TYPE_JSON,
    HEADER_CONTENT_TYPE: CONTENT_TYPE_JSON,
    HEADER_USER_AGENT: "API-Testing-Framework/2.0",
}

# API Endpoints (Example - JSONPlaceholder)
API_ENDPOINTS = {
    "posts": "/posts",
    "post_by_id": "/posts/{id}",
    "comments": "/comments",
    "albums": "/albums",
    "photos": "/photos",
    "todos": "/todos",
    "users": "/users",
    "user_by_id": "/users/{id}",
}

# Test Data Limits
MAX_RETRY_ATTEMPTS = 5
MAX_PAGE_SIZE = 100
MIN_PAGE_SIZE = 1

# Performance Thresholds (in seconds)
RESPONSE_TIME_THRESHOLD = 2.0
SLOW_RESPONSE_THRESHOLD = 5.0

# Validation
MAX_RESPONSE_SIZE_MB = 10
MIN_RESPONSE_SIZE_BYTES = 0

# Error Messages
ERROR_MSG_TIMEOUT = "Request timed out"
ERROR_MSG_CONNECTION = "Connection error"
ERROR_MSG_INVALID_JSON = "Invalid JSON response"
ERROR_MSG_SCHEMA_VALIDATION = "Schema validation failed"
ERROR_MSG_UNAUTHORIZED = "Unauthorized access"
ERROR_MSG_NOT_FOUND = "Resource not found"

# Logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Test Markers
MARKER_INTEGRATION = "integration"
MARKER_UNIT = "unit"
MARKER_E2E = "e2e"
MARKER_SLOW = "slow"
MARKER_ASYNCIO = "asyncio"
