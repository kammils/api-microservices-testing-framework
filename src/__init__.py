"""
API Microservices Testing Framework

Modern testing framework for API and microservices with Python, Pytest, and Httpx.
"""

__version__ = "2.0.0"

from src.api_client import APIClient
from src.config import APIConfig, get_config

__all__ = ["APIClient", "APIConfig", "get_config"]
