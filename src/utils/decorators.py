"""
Decorators Module

Provides utility decorators for retry logic, timeout handling, and test utilities.
"""

import asyncio
import functools
import time
from typing import Any, Callable, Optional, Tuple, Type, Union

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError,
)

from src.utils.logger import get_logger

logger = get_logger(__name__)


def retry_on_exception(
    max_attempts: int = 3,
    wait_multiplier: float = 1,
    wait_min: float = 1,
    wait_max: float = 10,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> Callable:
    """
    Decorator to retry function on specific exceptions with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        wait_multiplier: Multiplier for exponential backoff
        wait_min: Minimum wait time between retries (seconds)
        wait_max: Maximum wait time between retries (seconds)
        exceptions: Tuple of exception types to retry on
        
    Returns:
        Decorated function with retry logic
        
    Example:
        @retry_on_exception(max_attempts=3, exceptions=(ConnectionError,))
        def unstable_api_call():
            # API call that might fail
            pass
    """
    def decorator(func: Callable) -> Callable:
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=wait_multiplier, min=wait_min, max=wait_max),
            retry=retry_if_exception_type(exceptions),
            reraise=True,
        )
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except RetryError as e:
                logger.error(
                    f"Failed after {max_attempts} attempts: {func.__name__}",
                    context={"error": str(e)},
                    exc_info=True
                )
                raise
        
        return wrapper
    
    return decorator


def async_retry_on_exception(
    max_attempts: int = 3,
    wait_multiplier: float = 1,
    wait_min: float = 1,
    wait_max: float = 10,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> Callable:
    """
    Decorator to retry async function on specific exceptions with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        wait_multiplier: Multiplier for exponential backoff
        wait_min: Minimum wait time between retries (seconds)
        wait_max: Maximum wait time between retries (seconds)
        exceptions: Tuple of exception types to retry on
        
    Returns:
        Decorated async function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=wait_multiplier, min=wait_min, max=wait_max),
            retry=retry_if_exception_type(exceptions),
            reraise=True,
        )
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except RetryError as e:
                logger.error(
                    f"Async failed after {max_attempts} attempts: {func.__name__}",
                    context={"error": str(e)},
                    exc_info=True
                )
                raise
        
        return wrapper
    
    return decorator


def timeout(seconds: float) -> Callable:
    """
    Decorator to add timeout to synchronous functions.
    
    Args:
        seconds: Timeout in seconds
        
    Returns:
        Decorated function with timeout
        
    Example:
        @timeout(5)
        def long_running_task():
            # Task that might take too long
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            if elapsed > seconds:
                logger.warning(
                    f"Function {func.__name__} exceeded timeout",
                    context={"timeout": seconds, "elapsed": elapsed}
                )
            
            return result
        
        return wrapper
    
    return decorator


def async_timeout(seconds: float) -> Callable:
    """
    Decorator to add timeout to async functions.
    
    Args:
        seconds: Timeout in seconds
        
    Returns:
        Decorated async function with timeout
        
    Example:
        @async_timeout(5)
        async def long_running_task():
            # Async task that might take too long
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                logger.error(
                    f"Async function {func.__name__} timed out",
                    context={"timeout": seconds}
                )
                raise
        
        return wrapper
    
    return decorator


def log_execution_time(func: Callable) -> Callable:
    """
    Decorator to log function execution time.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function that logs execution time
        
    Example:
        @log_execution_time
        def some_function():
            # Function logic
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        
        logger.info(
            f"Executed {func.__name__}",
            context={"execution_time_ms": f"{elapsed * 1000:.2f}"}
        )
        
        return result
    
    return wrapper


def async_log_execution_time(func: Callable) -> Callable:
    """
    Decorator to log async function execution time.
    
    Args:
        func: Async function to decorate
        
    Returns:
        Decorated async function that logs execution time
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        result = await func(*args, **kwargs)
        elapsed = time.time() - start_time
        
        logger.info(
            f"Executed async {func.__name__}",
            context={"execution_time_ms": f"{elapsed * 1000:.2f}"}
        )
        
        return result
    
    return wrapper


def deprecated(message: str = "") -> Callable:
    """
    Decorator to mark functions as deprecated.
    
    Args:
        message: Optional deprecation message
        
    Returns:
        Decorated function that logs deprecation warning
        
    Example:
        @deprecated("Use new_function() instead")
        def old_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            warning_msg = f"Function {func.__name__} is deprecated."
            if message:
                warning_msg += f" {message}"
            
            logger.warning(warning_msg)
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator
