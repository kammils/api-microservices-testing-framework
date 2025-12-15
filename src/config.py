"""
Configuration Management Module

Handles loading and validation of configuration from environment variables
using Pydantic settings.
"""

import os
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class APIConfig(BaseSettings):
    """API Configuration"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Settings
    api_base_url: str = Field(default="http://localhost:8000", alias="API_BASE_URL")
    api_timeout: int = Field(default=30, alias="API_TIMEOUT")
    api_max_retries: int = Field(default=3, alias="API_MAX_RETRIES")
    api_backoff_factor: float = Field(default=0.5, alias="API_BACKOFF_FACTOR")
    api_verify_ssl: bool = Field(default=True, alias="API_VERIFY_SSL")

    # Authentication
    api_key: Optional[str] = Field(default=None, alias="API_KEY")
    api_secret: Optional[str] = Field(default=None, alias="API_SECRET")
    auth_token: Optional[str] = Field(default=None, alias="AUTH_TOKEN")

    # Test Configuration
    test_environment: str = Field(default="development", alias="TEST_ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    enable_detailed_logging: bool = Field(default=False, alias="ENABLE_DETAILED_LOGGING")

    # Microservices Endpoints
    user_service_url: str = Field(default="http://localhost:8001", alias="USER_SERVICE_URL")
    order_service_url: str = Field(default="http://localhost:8002", alias="ORDER_SERVICE_URL")
    product_service_url: str = Field(
        default="http://localhost:8003", alias="PRODUCT_SERVICE_URL"
    )

    # Test Data
    use_mock_data: bool = Field(default=True, alias="USE_MOCK_DATA")
    faker_locale: str = Field(default="en_US", alias="FAKER_LOCALE")
    faker_seed: Optional[int] = Field(default=12345, alias="FAKER_SEED")

    # Reporting
    allure_results_dir: str = Field(default="allure-results", alias="ALLURE_RESULTS_DIR")
    html_report_path: str = Field(default="reports/report.html", alias="HTML_REPORT_PATH")

    # Performance
    concurrent_requests: int = Field(default=10, alias="CONCURRENT_REQUESTS")
    request_rate_limit: int = Field(default=100, alias="REQUEST_RATE_LIMIT")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v_upper

    @field_validator("test_environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment"""
        valid_envs = ["development", "staging", "production", "testing"]
        v_lower = v.lower()
        if v_lower not in valid_envs:
            raise ValueError(f"Environment must be one of {valid_envs}")
        return v_lower

    @field_validator("api_timeout", "concurrent_requests", "request_rate_limit")
    @classmethod
    def validate_positive_int(cls, v: int) -> int:
        """Validate positive integers"""
        if v <= 0:
            raise ValueError("Value must be positive")
        return v


class TestConfig:
    """Test configuration singleton"""

    _instance = None
    _config: Optional[APIConfig] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TestConfig, cls).__new__(cls)
        return cls._instance

    @property
    def config(self) -> APIConfig:
        """Get configuration instance"""
        if self._config is None:
            self._config = APIConfig()
        return self._config

    def reload(self) -> None:
        """Reload configuration from environment"""
        self._config = APIConfig()


# Global configuration instance
def get_config() -> APIConfig:
    """Get global configuration instance"""
    return TestConfig().config


def reload_config() -> None:
    """Reload configuration"""
    TestConfig().reload()
