.PHONY: help install install-dev test test-unit test-integration test-e2e test-verbose coverage lint format clean setup

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install -r requirements.txt

install-dev:  ## Install dependencies including dev tools
	pip install -r requirements.txt
	pip install -e .

setup:  ## Setup the project (create venv, install deps, copy .env)
	python -m venv .venv
	@echo "Virtual environment created. Activate it with: source .venv/bin/activate (Linux/Mac) or .venv\\Scripts\\activate (Windows)"
	@if [ ! -f .env ]; then cp .env.example .env; echo ".env file created from .env.example"; fi

test:  ## Run all tests
	pytest

test-unit:  ## Run unit tests only
	pytest -m unit tests/unit/

test-integration:  ## Run integration tests only
	pytest -m integration tests/integration/

test-e2e:  ## Run end-to-end tests only
	pytest -m e2e tests/e2e/

test-verbose:  ## Run all tests with verbose output
	pytest -vv

test-smoke:  ## Run smoke tests
	pytest -m smoke

coverage:  ## Run tests with coverage report
	pytest --cov=src --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

coverage-report:  ## Open coverage report in browser
	@python -c "import webbrowser; webbrowser.open('htmlcov/index.html')"

lint:  ## Run linting with ruff
	ruff check src tests

lint-fix:  ## Run linting and auto-fix issues
	ruff check --fix src tests

format:  ## Format code with black
	black src tests

format-check:  ## Check code formatting without making changes
	black --check src tests

check:  ## Run all checks (lint + format check)
	ruff check src tests
	black --check src tests

allure-report:  ## Generate Allure report
	allure serve allure-results

html-report:  ## Open HTML test report
	@python -c "import webbrowser, os; webbrowser.open('file://' + os.path.abspath('reports/report.html'))"

clean:  ## Clean up generated files and caches
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf reports
	rm -rf allure-results
	rm -rf allure-report
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -rf .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.log" -delete

clean-all: clean  ## Clean everything including venv
	rm -rf .venv

run-example:  ## Run example API test
	python -m pytest tests/integration/test_microservices_api.py -v

watch:  ## Run tests in watch mode (requires pytest-watch)
	pytest-watch

# Quick commands
t: test  ## Shortcut for test
c: coverage  ## Shortcut for coverage
l: lint  ## Shortcut for lint
f: format  ## Shortcut for format
