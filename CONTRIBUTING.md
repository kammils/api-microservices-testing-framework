# Contributing to API Microservices Testing Framework

Thank you for your interest in contributing to the API Microservices Testing Framework! This document provides guidelines and instructions for contributing.

## 🤝 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Maintain professionalism in all interactions

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Familiarity with pytest and API testing concepts

### Setup Development Environment

1. **Fork and clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/api-microservices-testing-framework.git
cd api-microservices-testing-framework
```

2. **Create a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**

```bash
make install-dev
# Or manually:
pip install -r requirements.txt
pip install -e .
```

4. **Create a branch for your changes**

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

## 📝 Development Guidelines

### Code Style

We use **Black** for code formatting and **Ruff** for linting.

**Before committing:**

```bash
# Format code
make format

# Check linting
make lint

# Or run both
make check
```

**Code style rules:**

- Line length: 100 characters
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Keep functions focused and concise

### Naming Conventions

- **Functions/Methods**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`
- **Test functions**: `test_descriptive_name`

### Writing Tests

**Test organization:**

- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- E2E tests: `tests/e2e/`

**Test naming:**

```python
def test_feature_under_specific_condition():
    """Test description explaining what is being tested"""
    # Arrange
    # Act
    # Assert
```

**Use markers:**

```python
@pytest.mark.unit
def test_something():
    pass

@pytest.mark.integration
def test_api_endpoint():
    pass

@pytest.mark.e2e
def test_complete_flow():
    pass
```

**Run tests before committing:**

```bash
make test
make coverage
```

### Documentation

**Update documentation when:**

- Adding new features
- Changing existing functionality
- Adding new configuration options
- Creating new utilities or helpers

**Documentation locations:**

- Main README: High-level overview and quick start
- Code docstrings: Detailed function/class documentation
- CONTRIBUTING.md: Development guidelines

**Docstring format:**

```python
def function_name(param1: str, param2: int) -> dict:
    """
    Brief description of what the function does.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ExceptionType: When this exception is raised
    """
```

## 🔄 Contribution Workflow

### 1. Create an Issue

Before starting work, create or find an issue describing the change:

- Bug reports
- Feature requests
- Documentation improvements
- Code refactoring

### 2. Make Changes

- Write clean, well-documented code
- Follow the code style guidelines
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run all tests
make test

# Run specific test types
make test-unit
make test-integration

# Check coverage
make coverage

# Check code quality
make check
```

### 4. Commit Your Changes

**Commit message format:**

```
type: brief description

Longer description explaining the changes in more detail.

Fixes #issue-number
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**

```bash
git commit -m "feat: add async support to API client

Implemented async methods for all HTTP operations to support
concurrent API testing. Added context manager support for async
cleanup.

Closes #123"
```

```bash
git commit -m "fix: resolve retry logic issue with timeout

Fixed bug where retry logic wasn't respecting the configured
timeout value. Added test to prevent regression.

Fixes #456"
```

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:

- Clear description of changes
- Reference to related issues
- Screenshots (if applicable)
- Test results

## 🧪 Testing Guidelines

### Test Coverage

- Aim for >80% code coverage
- Write tests for all new features
- Include both positive and negative test cases
- Test edge cases and error conditions

### Test Structure

```python
import pytest
from src.api_client import APIClient

@pytest.mark.unit
class TestAPIClient:
    """Test suite for API Client"""

    def test_feature_works_correctly(self):
        """Test that feature works under normal conditions"""
        # Arrange
        client = APIClient(base_url="https://api.example.com")
        
        # Act
        result = client.get("/endpoint")
        
        # Assert
        assert result.status_code == 200
        client.close()

    def test_feature_handles_errors(self):
        """Test that feature handles errors gracefully"""
        # Test error conditions
        pass
```

### Fixtures

Use fixtures from `src/fixtures.py` or create new ones in `tests/conftest.py`:

```python
@pytest.fixture
def custom_client():
    """Provide custom configured client"""
    client = APIClient(base_url="https://custom.example.com")
    yield client
    client.close()
```

## 📦 Adding Dependencies

When adding new dependencies:

1. Add to `requirements.txt` with version constraint
2. Add to `pyproject.toml` in `dependencies` or `optional-dependencies`
3. Document why the dependency is needed
4. Check for security vulnerabilities
5. Prefer well-maintained, popular packages

## 🐛 Bug Reports

When reporting bugs, include:

- Python version
- Framework version
- Operating system
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages and stack traces
- Code samples (if applicable)

## 💡 Feature Requests

When requesting features:

- Describe the problem you're trying to solve
- Explain the proposed solution
- Provide use cases
- Consider alternative solutions
- Discuss potential impacts

## 📋 Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Code follows style guidelines (`make check`)
- [ ] All tests pass (`make test`)
- [ ] Coverage is maintained or improved (`make coverage`)
- [ ] Documentation is updated
- [ ] Commit messages are clear and descriptive
- [ ] PR description explains the changes
- [ ] Related issues are referenced
- [ ] No merge conflicts with main branch

## 🔍 Code Review Process

When your PR is submitted:

1. **Automated checks** will run (tests, linting, coverage)
2. **Maintainers** will review your code
3. **Feedback** may be provided for improvements
4. **Approval** is needed before merging
5. **Merge** will be done by maintainers

## ❓ Questions?

If you have questions:

- Check existing documentation
- Search closed issues
- Ask in a new issue with the `question` label
- Reach out to maintainers

## 🙏 Recognition

Contributors will be:

- Listed in release notes
- Credited in the project
- Acknowledged in the community

Thank you for contributing to make this framework better! 🎉

---

**Happy Contributing! 🚀**
