"""
Pytest Configuration and Fixtures

This module configures pytest and provides shared fixtures for all tests.
"""

import logging
import sys
from pathlib import Path

import pytest

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("test_logs.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

# Import fixtures from src.fixtures
pytest_plugins = ["src.fixtures"]


def pytest_configure(config):
    """Configure pytest"""
    logger.info("=" * 80)
    logger.info("Starting test session")
    logger.info("=" * 80)


def pytest_sessionfinish(session, exitstatus):
    """Clean up after test session"""
    logger.info("=" * 80)
    logger.info(f"Test session finished with exit status: {exitstatus}")
    logger.info("=" * 80)


# Custom markers
def pytest_collection_modifyitems(config, items):
    """Modify test items during collection"""
    for item in items:
        # Add markers based on test path
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
