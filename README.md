# API Microservices Testing Framework

A modern, production-ready framework for testing APIs and microservices, built with Python 3.11+, Pytest, and httpx.

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Features

- 🚀 **Modern Tech Stack**: Python 3.11+, Pytest, httpx (async-capable)
- 🔄 **Async Support**: Built-in asyncio support for concurrent testing
- 🔁 **Retry Logic**: Automatic retry with exponential backoff
- 📝 **Structured Logging**: Comprehensive request/response logging
- 🏭 **Test Data Generation**: Factory Boy + Faker for realistic test data
- ✅ **Schema Validation**: JSON schema validation for API responses
- 📊 **Rich Reporting**: HTML reports, Allure reports, coverage reports
- 🎯 **Custom Assertions**: API-specific assertion helpers
- ⚙️ **Configuration Management**: Environment-based settings with pydantic
- 🧪 **Multiple Test Types**: Unit, integration, and E2E tests
- 🛠️ **Code Quality**: Black, Ruff, MyPy for code quality
- 🔐 **Security Scanning**: Bandit and Safety checks
- 📦 **CI/CD Ready**: GitHub Actions workflows included

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Usage](#usage)
- [Running Tests](#running-tests)
- [API Client](#api-client)
- [Test Data Factories](#test-data-factories)
- [Custom Assertions](#custom-assertions)
- [Schema Validation](#schema-validation)
- [Decorators](#decorators)
- [Reporting](#reporting)
- [CI/CD](#cicd)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites

- Python 3.11 or higher
- pip or poetry for package management

### Install Dependencies

```bash
# Clone the repository
git clone https://github.com/yourusername/api-microservices-testing-framework.git
cd api-microservices-testing-framework

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### Using Make

```bash
# Setup everything
make setup

# Or install individually
make install       # Production dependencies only
make install-dev   # Development dependencies
```

## Quick Start

### 1. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API settings
nano .env
```

### 2. Run Your First Test

```python
# tests/test_example.py
import pytest
from src.clients.api_client import APIClient
from src.utils.assertions import assert_status_code

def test_get_posts(api_client):
    """Test getting all posts."""
    response = api_client.get("/posts")
    assert_status_code(response, 200)
    
    posts = response.json()
    assert len(posts) > 0
```

### 3. Execute Tests

```bash
# Run all tests
pytest

# Run specific test types
pytest tests/unit -v
pytest tests/integration -v
pytest tests/e2e -v

# Run with coverage
pytest --cov=src --cov-report=html
```

## Project Structure

```
api-microservices-testing-framework/
├── .github/
│   └── workflows/
│       └── tests.yml                 # CI/CD pipeline
├── src/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py               # Environment configuration
│   │   └── constants.py              # Test constants
│   ├── clients/
│   │   ├── __init__.py
│   │   └── api_client.py             # httpx-based API client
│   ├── fixtures/
│   │   ├── __init__.py
│   │   ├── factories.py              # Factory Boy data factories
│   │   └── conftest.py               # Pytest fixtures
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py                 # Structured logging
│   │   ├── assertions.py             # Custom assertions
│   │   └── decorators.py             # Retry, timeout decorators
│   └── validators/
│       ├── __init__.py
│       └── schema_validator.py       # JSON schema validation
├── tests/
│   ├── __init__.py
│   ├── integration/                  # Integration tests
│   │   ├── __init__.py
│   │   ├── test_api_endpoints.py
│   │   └── test_microservices.py
│   ├── unit/                         # Unit tests
│   │   ├── __init__.py
│   │   └── test_utilities.py
│   └── e2e/                          # End-to-end tests
│       ├── __init__.py
│       └── test_workflows.py
├── .env.example                      # Example environment file
├── .env                              # Your environment settings
├── .gitignore
├── pyproject.toml                    # Project configuration
├── pytest.ini                        # Pytest configuration
├── requirements.txt                  # Production dependencies
├── requirements-dev.txt              # Development dependencies
├── conftest.py                       # Root pytest config
├── Makefile                          # Common commands
├── README.md                         # This file
└── CONTRIBUTING.md                   # Contribution guidelines
```

## Configuration

### Environment Variables

Configure the framework via `.env` file or environment variables:

```bash
# API Configuration
API_BASE_URL=https://api.example.com
API_TIMEOUT=30
API_MAX_RETRIES=3
API_BACKOFF_FACTOR=0.5

# Authentication
API_KEY=your_api_key
AUTH_TOKEN=your_token

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
DEBUG=true

# Feature Flags
ENABLE_RETRY=true
ENABLE_ASYNC=true
VERIFY_SSL=true
```

### Settings Module

Access settings in your code:

```python
from src.config.settings import settings

# Use settings
base_url = settings.api_base_url
timeout = settings.api_timeout

# Check environment
if settings.is_production():
    # Production-specific logic
    pass
```

## Usage

### API Client

The framework provides a powerful httpx-based API client with sync and async support:

```python
from src.clients.api_client import APIClient

# Create client
client = APIClient(base_url="https://api.example.com")

# Synchronous requests
response = client.get("/users")
response = client.post("/users", json={"name": "John"})
response = client.put("/users/1", json={"name": "Jane"})
response = client.patch("/users/1", json={"email": "jane@example.com"})
response = client.delete("/users/1")

# Async requests
async def test_async():
    async with APIClient() as client:
        response = await client.get_async("/users")
        return response.json()

# Authentication
client.set_auth_header("Bearer", "your_token")

# Custom headers
client.set_header("X-Custom-Header", "value")
```

### Test Data Factories

Generate realistic test data with Factory Boy:

```python
from src.fixtures.factories import UserFactory, PostFactory, generate_users

# Generate single items
user = UserFactory()
post = PostFactory()

# Generate multiple items
users = generate_users(count=10)

# Use in tests
def test_create_user(api_client):
    user_data = UserFactory()
    response = api_client.post("/users", json=user_data)
    assert response.status_code == 201
```

### Custom Assertions

Use built-in assertion helpers for cleaner test code:

```python
from src.utils.assertions import (
    assert_status_code,
    assert_response_time,
    assert_json_contains,
    assert_successful_response,
)

def test_api_response(api_client):
    response = api_client.get("/users/1")
    
    # Assert status
    assert_status_code(response, 200)
    assert_successful_response(response)
    
    # Assert performance
    assert_response_time(response, max_time_seconds=2.0)
    
    # Assert response structure
    user = response.json()
    assert_json_contains(user, ["id", "name", "email"])
```

### Schema Validation

Validate API responses against JSON schemas:

```python
from src.validators.schema_validator import SchemaValidator, COMMON_SCHEMAS

validator = SchemaValidator()

def test_user_schema(api_client):
    response = api_client.get("/users/1")
    user = response.json()
    
    # Validate against predefined schema
    validator.validate(user, COMMON_SCHEMAS["user"])
    
    # Create custom schema
    custom_schema = SchemaValidator.create_object_schema(
        properties={
            "id": {"type": "integer"},
            "name": {"type": "string"},
        },
        required=["id", "name"]
    )
    validator.validate(user, custom_schema)
```

### Decorators

Utilize decorators for retry logic and timeouts:

```python
from src.utils.decorators import retry_on_exception, async_timeout

# Retry on failures
@retry_on_exception(max_attempts=3, exceptions=(ConnectionError,))
def unstable_operation():
    # Operation that might fail
    pass

# Async timeout
@async_timeout(5)
async def long_running_task():
    # Task with timeout
    pass
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/integration/test_api_endpoints.py

# Run specific test
pytest tests/integration/test_api_endpoints.py::TestPostsEndpoint::test_get_all_posts
```

### Test by Marker

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only e2e tests
pytest -m e2e

# Run slow tests
pytest -m slow

# Run async tests
pytest -m asyncio
```

### Using Make

```bash
make test              # Run all tests
make test-unit         # Unit tests only
make test-integration  # Integration tests only
make test-e2e          # E2E tests only
make test-cov          # Tests with coverage
```

### Coverage Reports

```bash
# Generate coverage report
pytest --cov=src --cov-report=html --cov-report=term-missing

# Open HTML report
open htmlcov/index.html
```

## Reporting

### HTML Reports

```bash
# Generate HTML report
pytest --html=reports/report.html --self-contained-html

# Using Make
make test-html
```

### Allure Reports

```bash
# Generate Allure results
pytest --alluredir=allure-results

# Serve Allure report
allure serve allure-results

# Using Make
make test-allure
```

### Coverage Reports

Coverage reports are automatically generated in `htmlcov/` directory when running tests with coverage.

## CI/CD

The framework includes GitHub Actions workflow for continuous integration:

- ✅ Runs tests on Python 3.11 and 3.12
- ✅ Linting with Ruff
- ✅ Formatting check with Black
- ✅ Type checking with MyPy
- ✅ Security scanning with Bandit and Safety
- ✅ Code coverage reporting
- ✅ Test result artifacts

### Workflow File

See `.github/workflows/tests.yml` for the complete CI/CD configuration.

## Code Quality

### Format Code

```bash
# Format with Black
black src tests

# Sort imports with Ruff
ruff check --fix src tests

# Using Make
make format
```

### Lint Code

```bash
# Lint with Ruff
ruff check src tests

# Type check with MyPy
mypy src

# Using Make
make lint
```

## Best Practices

1. **Use Fixtures**: Leverage pytest fixtures for reusable test setup
2. **Test Isolation**: Keep tests independent and idempotent
3. **Meaningful Names**: Use descriptive test names that explain what is being tested
4. **Async When Needed**: Use async for parallel operations, sync for simplicity
5. **Schema Validation**: Always validate API response schemas
6. **Proper Assertions**: Use custom assertions for better error messages
7. **Environment Configuration**: Use environment variables for configuration
8. **Logging**: Enable structured logging for debugging
9. **Coverage**: Aim for high test coverage (>80%)
10. **Documentation**: Document complex test scenarios

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure src is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}"
```

**SSL Certificate Errors**
```bash
# Disable SSL verification (not recommended for production)
VERIFY_SSL=false pytest
```

**Timeout Errors**
```bash
# Increase timeout in .env
API_TIMEOUT=60
```

## Examples

See the `tests/` directory for comprehensive examples:

- **Unit Tests**: `tests/unit/test_utilities.py`
- **Integration Tests**: `tests/integration/test_api_endpoints.py`
- **Microservices Tests**: `tests/integration/test_microservices.py`
- **E2E Workflows**: `tests/e2e/test_workflows.py`

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation
- Review example tests

## Changelog

### Version 2.0.0
- Complete rebuild with modern tech stack
- httpx-based async client
- Enhanced fixtures and factories
- Comprehensive test examples
- CI/CD with GitHub Actions
- Improved documentation

---

**Made with ❤️ for API Testing**
