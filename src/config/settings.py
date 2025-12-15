"""
Application Settings Module

Manages environment-based configuration using pydantic-settings.
Loads configuration from environment variables and .env files.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Uses pydantic-settings for validation and type conversion.
    Automatically loads from .env file if present.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )
    
    # API Configuration
    api_base_url: str = Field(
        default="https://jsonplaceholder.typicode.com",
        description="Base URL for API endpoints"
    )
    api_timeout: int = Field(
        default=30,
        description="Request timeout in seconds"
    )
    api_max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts"
    )
    api_backoff_factor: float = Field(
        default=0.5,
        description="Backoff factor for exponential retry"
    )
    
    # Authentication
    api_key: Optional[str] = Field(
        default=None,
        description="API key for authentication"
    )
    api_secret: Optional[str] = Field(
        default=None,
        description="API secret for authentication"
    )
    auth_token: Optional[str] = Field(
        default=None,
        description="Bearer token for authentication"
    )
    
    # Environment
    environment: str = Field(
        default="development",
        description="Current environment (development, staging, production)"
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    debug: bool = Field(
        default=True,
        description="Enable debug mode"
    )
    
    # Feature Flags
    enable_retry: bool = Field(
        default=True,
        description="Enable retry mechanism"
    )
    enable_async: bool = Field(
        default=True,
        description="Enable async support"
    )
    verify_ssl: bool = Field(
        default=True,
        description="Verify SSL certificates"
    )
    
    # Reporting
    allure_results_dir: str = Field(
        default="allure-results",
        description="Directory for Allure results"
    )
    html_report_dir: str = Field(
        default="reports",
        description="Directory for HTML reports"
    )
    
    # Test Configuration
    test_user_email: Optional[str] = Field(
        default=None,
        description="Test user email"
    )
    test_user_password: Optional[str] = Field(
        default=None,
        description="Test user password"
    )
    
    # External Services
    external_service_url: Optional[str] = Field(
        default=None,
        description="External service URL"
    )
    external_service_key: Optional[str] = Field(
        default=None,
        description="External service API key"
    )
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self.environment.lower() == "staging"


# Global settings instance
settings = Settings()
