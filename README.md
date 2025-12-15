# API Microservices Testing Framework

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Pytest](https://img.shields.io/badge/testing-pytest-green.svg)](https://pytest.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/linter-ruff-orange.svg)](https://github.com/astral-sh/ruff)

A modern, production-ready API and microservices testing framework built with Python, Pytest, and Httpx. This framework provides a comprehensive solution for testing RESTful APIs and microservices architectures with async support, retry logic, and extensive reporting capabilities.

## ✨ Features

- 🚀 **Modern Tech Stack** - Python 3.11+, Pytest, Httpx (async-capable)
- 🔄 **Retry Logic** - Automatic retry with exponential backoff
- 📊 **Rich Reporting** - Pytest-HTML and Allure Reports
- 🏭 **Test Data Generation** - Factory Boy + Faker for realistic test data
- ✅ **Custom Assertions** - Comprehensive assertion helpers for API testing
- 🔐 **Security** - Built-in sensitive data masking and SSL verification
- 🎯 **Test Organization** - Structured by type (unit, integration, e2e)
- ⚡ **Async Support** - Full async/await support for concurrent testing
- 🛠️ **Developer Tools** - Black formatting, Ruff linting, coverage reporting
- 🔧 **Configuration** - Environment-based config with python-dotenv
- 📝 **Comprehensive Logging** - Structured logging with configurable levels
- 🤖 **CI/CD Ready** - GitHub Actions workflow included

## 📋 Requirements

- Python 3.11 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/kammils/api-microservices-testing-framework.git
cd api-microservices-testing-framework
```

### 2. Setup Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install all dependencies
make install

# Or manually:
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use your preferred editor
```

### 5. Run Tests

```bash
# Run all tests
make test

# Run specific test types
make test-unit
make test-integration
make test-e2e

# Run with coverage
make coverage
```

## 📁 Project Structure

```
api-microservices-testing-framework/
├── src/                          # Source code
│   ├── __init__.py
│   ├── api_client.py            # Modern Httpx-based API client
│   ├── config.py                # Configuration management with Pydantic
│   ├── assertions.py            # Custom assertion helpers
│   ├── fixtures.py              # Pytest fixtures
│   ├── factories.py             # Factory Boy factories for test data
│   └── utils.py                 # Utility functions
├── tests/                        # Test directory
│   ├── conftest.py              # Pytest configuration
│   ├── unit/                    # Unit tests
│   │   └── test_api_client.py
│   ├── integration/             # Integration tests
│   │   └── test_microservices_api.py
│   ├── e2e/                     # End-to-end tests
│   │   └── test_full_flow.py
│   └── data/                    # Test data
│       └── fixtures.json
├── .github/                     # GitHub configuration
│   └── workflows/
│       └── test.yml             # CI/CD workflow
├── reports/                     # Test reports (generated)
├── htmlcov/                     # Coverage reports (generated)
├── pyproject.toml               # Project configuration
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration
├── Makefile                     # Common commands
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── README.md                    # This file
└── CONTRIBUTING.md              # Contribution guidelines
```

## 🎯 Usage Examples

### Basic API Client Usage

```python
from src.api_client import APIClient

# Create client
client = APIClient(base_url="https://api.example.com")

# Make requests
response = client.get("/users")
response = client.post("/users", json={"name": "John Doe"})

# With context manager
with APIClient(base_url="https://api.example.com") as client:
    response = client.get("/users")
```

### Async API Client Usage

```python
import asyncio
from src.api_client import APIClient

async def test_async():
    client = APIClient(base_url="https://api.example.com")
    
    # Async requests
    response = await client.get_async("/users")
    response = await client.post_async("/users", json={"name": "Jane"})
    
    await client.close_async()

asyncio.run(test_async())
```

### Using Factories for Test Data

```python
from src.factories import generate_user, generate_users

# Generate single user
user = generate_user()

# Generate multiple users
users = generate_users(count=10)

# Generate with overrides
user = generate_user(email="custom@example.com", age=25)
```

### Using Custom Assertions

```python
from src import assertions

# Assert status code
assertions.assert_status_code(response, 200)

# Assert response time
assertions.assert_response_time(response, max_time=2.0)

# Assert JSON structure
assertions.assert_json_has_keys(response, ["id", "name", "email"])

# Assert content type
assertions.assert_content_type(response, "application/json")
```

### Writing Tests

```python
import pytest
from src import assertions

@pytest.mark.integration
def test_get_users(api_client):
    """Test getting list of users"""
    response = api_client.get("/users")
    
    assertions.assert_status_code(response, 200)
    assertions.assert_json_response(response)
    
    users = response.json()
    assert isinstance(users, list)
```

## 🧪 Running Tests

### Using Make Commands

```bash
# Run all tests
make test

# Run specific test types
make test-unit          # Unit tests only
make test-integration   # Integration tests only
make test-e2e          # End-to-end tests only
make test-smoke        # Smoke tests only

# Run with verbose output
make test-verbose

# Generate coverage report
make coverage

# Open coverage report in browser
make coverage-report
```

### Using Pytest Directly

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_api_client.py

# Run tests with marker
pytest -m unit
pytest -m integration
pytest -m e2e

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/unit/test_api_client.py::TestAPIClientInitialization::test_client_initialization_with_defaults
```

## 🔧 Configuration

### Environment Variables

Configure the framework using environment variables in `.env`:

```bash
# API Configuration
API_BASE_URL=http://localhost:8000
API_TIMEOUT=30
API_MAX_RETRIES=3
API_VERIFY_SSL=true

# Authentication
API_KEY=your_api_key_here
AUTH_TOKEN=your_auth_token_here

# Test Configuration
TEST_ENVIRONMENT=development
LOG_LEVEL=INFO

# Microservices Endpoints
USER_SERVICE_URL=http://localhost:8001
ORDER_SERVICE_URL=http://localhost:8002
PRODUCT_SERVICE_URL=http://localhost:8003
```

### Pytest Configuration

Configure pytest in `pytest.ini`:

```ini
[pytest]
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    smoke: Smoke tests
    slow: Slow running tests
```

## 📊 Reports

### HTML Report

After running tests, open the HTML report:

```bash
# Generate and open HTML report
make html-report

# Or manually
open reports/report.html
```

### Coverage Report

Generate and view coverage:

```bash
# Generate coverage report
make coverage

# Open in browser
make coverage-report
```

### Allure Report

Generate Allure reports:

```bash
# Run tests with Allure
pytest --alluredir=allure-results

# Generate and serve Allure report
make allure-report
```

## 🎨 Code Quality

### Formatting

```bash
# Format code with Black
make format

# Check formatting without changes
make format-check
```

### Linting

```bash
# Run linting
make lint

# Run linting with auto-fix
make lint-fix
```

### Run All Checks

```bash
# Run both linting and format check
make check
```

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [documentation](README.md)
2. Search [existing issues](https://github.com/kammils/api-microservices-testing-framework/issues)
3. Create a [new issue](https://github.com/kammils/api-microservices-testing-framework/issues/new)

## 🔗 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Httpx Documentation](https://www.python-httpx.org/)
- [Factory Boy Documentation](https://factoryboy.readthedocs.io/)
- [Faker Documentation](https://faker.readthedocs.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## 📈 Roadmap

- [ ] Add performance testing support
- [ ] Add contract testing support
- [ ] Add GraphQL support
- [ ] Add WebSocket testing support
- [ ] Add test data seeding utilities
- [ ] Add Docker support
- [ ] Add more example tests

---

**Built with ❤️ by the API Testing Framework Team**
