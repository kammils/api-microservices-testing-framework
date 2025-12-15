.PHONY: help install install-dev test test-unit test-integration test-e2e test-cov lint format clean run-example

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -r requirements-dev.txt

test:  ## Run all tests
	pytest

test-unit:  ## Run unit tests only
	pytest tests/unit -v

test-integration:  ## Run integration tests only
	pytest tests/integration -v

test-e2e:  ## Run e2e tests only
	pytest tests/e2e -v

test-cov:  ## Run tests with coverage report
	pytest --cov=src --cov-report=html --cov-report=term-missing

test-html:  ## Run tests and generate HTML report
	pytest --html=reports/report.html --self-contained-html

test-allure:  ## Run tests with Allure reporting
	pytest --alluredir=allure-results
	allure serve allure-results

lint:  ## Run linters (ruff and mypy)
	ruff check src tests
	mypy src

format:  ## Format code with black and ruff
	black src tests
	ruff check --fix src tests

format-check:  ## Check code formatting without making changes
	black --check src tests
	ruff check src tests

clean:  ## Clean up generated files
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf allure-results
	rm -rf allure-report
	rm -rf reports
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.log" -delete

venv:  ## Create virtual environment
	python -m venv venv
	@echo "Virtual environment created. Activate with: source venv/bin/activate"

setup:  ## Initial setup (create venv and install dependencies)
	python -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements-dev.txt
	@echo "Setup complete! Activate venv with: source venv/bin/activate"

pre-commit:  ## Run pre-commit checks
	black src tests
	ruff check --fix src tests
	mypy src
	pytest tests/unit -v

ci:  ## Run CI pipeline locally
	make format-check
	make lint
	make test-cov

.DEFAULT_GOAL := help
