# Contributing to API Microservices Testing Framework

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Virtual environment tool (venv, virtualenv, or conda)
- Familiarity with pytest and API testing

### Development Setup

1. **Fork the repository**

   Click the "Fork" button on GitHub to create your own copy.

2. **Clone your fork**

   ```bash
   git clone https://github.com/your-username/api-microservices-testing-framework.git
   cd api-microservices-testing-framework
   ```

3. **Set up the development environment**

   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements-dev.txt

   # Or use Make
   make setup
   ```

4. **Create a feature branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

1. **Bug Fixes**: Fix issues or bugs in the codebase
2. **New Features**: Add new functionality or capabilities
3. **Documentation**: Improve or add documentation
4. **Tests**: Add or improve test coverage
5. **Examples**: Add example tests or use cases
6. **Refactoring**: Improve code quality or structure

### Contribution Workflow

1. **Find or Create an Issue**
   - Check existing issues for something to work on
   - Create a new issue if needed
   - Comment on the issue to let others know you're working on it

2. **Create a Branch**
   ```bash
   git checkout -b feature/issue-number-description
   ```

3. **Make Your Changes**
   - Write code following our coding standards
   - Add tests for new functionality
   - Update documentation as needed

4. **Test Your Changes**
   ```bash
   # Run all tests
   make test

   # Run linters
   make lint

   # Format code
   make format
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

   Use conventional commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `test:` for test additions/changes
   - `refactor:` for code refactoring
   - `chore:` for maintenance tasks

6. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill in the PR template
   - Submit the PR

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line Length**: Maximum 100 characters (configured in Black)
- **Formatting**: Use Black for code formatting
- **Import Sorting**: Use Ruff for import sorting
- **Type Hints**: Use type hints for function signatures
- **Docstrings**: Use Google-style docstrings

### Code Formatting

```bash
# Format code
black src tests

# Sort imports
ruff check --fix src tests

# Or use Make
make format
```

### Linting

```bash
# Run Ruff
ruff check src tests

# Run MyPy
mypy src

# Or use Make
make lint
```

### Example Code Style

```python
from typing import Dict, List, Optional


def fetch_user_data(
    user_id: int,
    include_posts: bool = False,
    max_posts: Optional[int] = None
) -> Dict[str, Any]:
    """
    Fetch user data from the API.
    
    Args:
        user_id: The ID of the user to fetch
        include_posts: Whether to include user's posts
        max_posts: Maximum number of posts to include
        
    Returns:
        Dictionary containing user data
        
    Raises:
        ValueError: If user_id is invalid
        APIError: If API request fails
    """
    if user_id < 1:
        raise ValueError("user_id must be positive")
    
    # Implementation
    pass
```

## Testing Guidelines

### Writing Tests

1. **Test Structure**
   - Use descriptive test names: `test_<what_is_being_tested>`
   - Group related tests in classes
   - Use appropriate markers (`@pytest.mark.unit`, etc.)

2. **Test Organization**
   ```python
   import pytest
   from src.clients.api_client import APIClient
   
   
   @pytest.mark.integration
   class TestUserEndpoints:
       """Test user-related endpoints."""
       
       def test_get_user_by_id(self, api_client):
           """Test retrieving a user by ID."""
           # Arrange
           user_id = 1
           
           # Act
           response = api_client.get(f"/users/{user_id}")
           
           # Assert
           assert response.status_code == 200
           assert response.json()["id"] == user_id
   ```

3. **Use Fixtures**
   - Leverage existing fixtures from `conftest.py`
   - Create new fixtures for reusable test setup
   - Use appropriate fixture scopes

4. **Test Coverage**
   - Aim for >80% code coverage
   - Write tests for edge cases
   - Test both success and failure scenarios

### Running Tests

```bash
# Run all tests
pytest

# Run specific test types
pytest -m unit
pytest -m integration
pytest -m e2e

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_utilities.py

# Using Make
make test
make test-unit
make test-cov
```

### Test Categories

- **Unit Tests**: Test individual functions/classes in isolation
- **Integration Tests**: Test API endpoints and integrations
- **E2E Tests**: Test complete workflows and scenarios

## Submitting Changes

### Pull Request Guidelines

1. **PR Title**: Use conventional commit format
   - `feat: add user authentication`
   - `fix: resolve timeout issue in API client`
   - `docs: update README with examples`

2. **PR Description**: Include:
   - What changes were made
   - Why the changes were needed
   - How to test the changes
   - Related issue numbers

3. **PR Checklist**:
   - [ ] Code follows the style guidelines
   - [ ] Tests have been added/updated
   - [ ] All tests pass locally
   - [ ] Documentation has been updated
   - [ ] No new linting errors introduced
   - [ ] Commit messages follow conventions

### Review Process

1. Automated checks will run (CI/CD)
2. Maintainers will review your PR
3. Address any feedback or requested changes
4. Once approved, a maintainer will merge your PR

### After Your PR is Merged

1. Delete your feature branch
2. Pull the latest changes from main
3. Thank you for contributing! 🎉

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Detailed steps to reproduce the issue
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**:
   - Python version
   - Operating system
   - Relevant dependencies versions
6. **Logs/Screenshots**: Any relevant logs or screenshots

### Feature Requests

When requesting features, please include:

1. **Description**: Clear description of the feature
2. **Use Case**: Why this feature would be useful
3. **Proposed Solution**: How you envision the feature working
4. **Alternatives**: Any alternative solutions considered

## Documentation

### Updating Documentation

- Update README.md for user-facing changes
- Update docstrings for code changes
- Add examples for new features
- Update CONTRIBUTING.md for process changes

### Documentation Style

- Use clear, concise language
- Include code examples
- Add comments for complex logic
- Keep documentation up-to-date with code

## Community

### Getting Help

- Check existing documentation
- Search through issues
- Ask questions in discussions
- Reach out to maintainers

### Communication

- Be respectful and professional
- Provide context in communications
- Be patient with responses
- Help others when you can

## Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes
- Project documentation

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.

## Questions?

If you have questions about contributing, please:
1. Check this document
2. Search existing issues
3. Create a new issue with the "question" label

---

Thank you for contributing to the API Microservices Testing Framework! 🚀
