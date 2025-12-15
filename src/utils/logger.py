"""
Structured Logging Module

Provides structured logging with context, formatting, and log levels.
Supports both console and file logging with JSON formatting options.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from src.config.settings import settings
from src.config.constants import LOG_FORMAT, LOG_DATE_FORMAT


class StructuredLogger:
    """
    Structured logger with support for context and custom formatting.
    
    Features:
    - Console and file logging
    - Structured log messages with context
    - Log levels based on configuration
    - Automatic log file rotation
    """
    
    def __init__(
        self,
        name: str,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
        enable_console: bool = True,
    ):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name (typically __name__)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional log file path
            enable_console: Enable console logging
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level or settings.log_level)
        self.logger.propagate = False
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Formatter
        formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        
        # Console handler
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(log_level or settings.log_level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def _format_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Format message with optional context."""
        if context:
            context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
            return f"{message} | {context_str}"
        return message
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log debug message."""
        self.logger.debug(self._format_message(message, context))
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log info message."""
        self.logger.info(self._format_message(message, context))
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log warning message."""
        self.logger.warning(self._format_message(message, context))
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None, exc_info: bool = False) -> None:
        """Log error message."""
        self.logger.error(self._format_message(message, context), exc_info=exc_info)
    
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None, exc_info: bool = False) -> None:
        """Log critical message."""
        self.logger.critical(self._format_message(message, context), exc_info=exc_info)
    
    def log_request(
        self,
        method: str,
        url: str,
        status_code: Optional[int] = None,
        response_time: Optional[float] = None,
    ) -> None:
        """
        Log HTTP request with details.
        
        Args:
            method: HTTP method
            url: Request URL
            status_code: Response status code
            response_time: Response time in seconds
        """
        context = {
            "method": method,
            "url": url,
        }
        
        if status_code:
            context["status_code"] = status_code
        
        if response_time:
            context["response_time_ms"] = f"{response_time * 1000:.2f}"
        
        self.info(f"HTTP Request: {method} {url}", context)
    
    def log_test_start(self, test_name: str) -> None:
        """Log test execution start."""
        self.info(f"Starting test: {test_name}")
    
    def log_test_end(self, test_name: str, status: str, duration: Optional[float] = None) -> None:
        """
        Log test execution end.
        
        Args:
            test_name: Name of the test
            status: Test status (PASSED, FAILED, SKIPPED)
            duration: Test duration in seconds
        """
        context = {"status": status}
        if duration:
            context["duration_ms"] = f"{duration * 1000:.2f}"
        
        self.info(f"Completed test: {test_name}", context)


def get_logger(
    name: str,
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
) -> StructuredLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name
        log_level: Optional log level override
        log_file: Optional log file path
        
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name=name, log_level=log_level, log_file=log_file)


# Default logger instance
logger = get_logger(__name__)
