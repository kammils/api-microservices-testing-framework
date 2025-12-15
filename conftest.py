import pytest
import logging
from typing import Dict, Any
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_logs.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def test_config():
    """Load test configuration from environment variables"""
    return {
        "base_url": os.getenv("API_BASE_URL", "http://localhost:8000"),
        "timeout": int(os.getenv("API_TIMEOUT", "30")),
        "retry_count": int(os.getenv("RETRY_COUNT", "3")),
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
    }


@pytest.fixture
def logger_fixture():
    """Provide logger to tests"""
    return logger


@pytest.fixture(autouse=True)
def log_test_info(request):
    """Log test execution info"""
    logger.info(f"Starting test: {request.node.name}")
    yield
    logger.info(f"Completed test: {request.node.name}")