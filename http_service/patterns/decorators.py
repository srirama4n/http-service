"""
Decorators for HTTP client functionality.
Contains retry logic and rate limiting decorators.
"""

import asyncio
import time
import logging
from typing import Callable, Optional, Any
from functools import wraps
import httpx

logger = logging.getLogger(__name__)


def retry(
    max_retries: int = 3,
    retry_delay: float = 1.0,
    backoff_factor: float = 2.0,
    retry_on_exceptions: Optional[list] = None,
    retry_on_status_codes: Optional[list] = None
):
    """
    Decorator to add retry logic to functions.
    
    Args:
        max_retries: Maximum number of retry attempts
        retry_delay: Initial delay between retries
        backoff_factor: Multiplier for exponential backoff
        retry_on_exceptions: List of exception types to retry on
        retry_on_status_codes: List of HTTP status codes to retry on
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    
                    # Check if response indicates retry is needed
                    if hasattr(result, 'status_code') and retry_on_status_codes:
                        if result.status_code in retry_on_status_codes:
                            if attempt < max_retries:
                                delay = retry_delay * (backoff_factor ** attempt)
                                logger.warning(f"Retrying {func.__name__} after {delay}s due to status {result.status_code}")
                                time.sleep(delay)
                                continue
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    should_retry = False
                    
                    # Default behavior: retry on all exceptions unless specific ones are specified
                    if retry_on_exceptions:
                        should_retry = any(isinstance(e, exc_type) for exc_type in retry_on_exceptions)
                    else:
                        should_retry = True
                    
                    if should_retry and attempt < max_retries:
                        delay = retry_delay * (backoff_factor ** attempt)
                        logger.warning(f"Retrying {func.__name__} after {delay}s due to {type(e).__name__}: {e}")
                        time.sleep(delay)
                        continue
                    else:
                        break
            
            if last_exception:
                logger.error(f"Function {func.__name__} failed after {max_retries + 1} attempts")
                raise last_exception
        
        return wrapper
    return decorator


def async_retry(
    max_retries: int = 3,
    retry_delay: float = 1.0,
    backoff_factor: float = 2.0,
    retry_on_exceptions: Optional[list] = None,
    retry_on_status_codes: Optional[list] = None
):
    """
    Decorator to add retry logic to async functions.
    
    Args:
        max_retries: Maximum number of retry attempts
        retry_delay: Initial delay between retries
        backoff_factor: Multiplier for exponential backoff
        retry_on_exceptions: List of exception types to retry on
        retry_on_status_codes: List of HTTP status codes to retry on
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    result = await func(*args, **kwargs)
                    
                    # Check if response indicates retry is needed
                    if hasattr(result, 'status_code') and retry_on_status_codes:
                        if result.status_code in retry_on_status_codes:
                            if attempt < max_retries:
                                delay = retry_delay * (backoff_factor ** attempt)
                                logger.warning(f"Retrying {func.__name__} after {delay}s due to status {result.status_code}")
                                await asyncio.sleep(delay)
                                continue
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    should_retry = False
                    
                    # Default behavior: retry on all exceptions unless specific ones are specified
                    if retry_on_exceptions:
                        should_retry = any(isinstance(e, exc_type) for exc_type in retry_on_exceptions)
                    else:
                        should_retry = True
                    
                    if should_retry and attempt < max_retries:
                        delay = retry_delay * (backoff_factor ** attempt)
                        logger.warning(f"Retrying {func.__name__} after {delay}s due to {type(e).__name__}: {e}")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        break
            
            if last_exception:
                logger.error(f"Function {func.__name__} failed after {max_retries + 1} attempts")
                raise last_exception
        
        return wrapper
    return decorator


def rate_limit(requests_per_second: Optional[float] = None, burst_size: int = 1):
    """
    Decorator to add rate limiting to functions.
    
    Args:
        requests_per_second: Maximum requests per second (None for no limit)
        burst_size: Number of requests allowed in burst
    """
    def decorator(func: Callable) -> Callable:
        last_request_time = 0
        request_count = 0
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal last_request_time, request_count
            
            # If no rate limiting, just call the function
            if requests_per_second is None:
                return func(*args, **kwargs)
            
            current_time = time.time()
            time_since_last_request = current_time - last_request_time
            min_interval = 1.0 / requests_per_second
            
            # Reset burst counter if enough time has passed
            if time_since_last_request >= min_interval:
                request_count = 0
            
            # Check if we need to wait
            if request_count >= burst_size:
                sleep_time = min_interval - time_since_last_request
                if sleep_time > 0:
                    time.sleep(sleep_time)
                request_count = 0
            
            request_count += 1
            last_request_time = time.time()
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def async_rate_limit(requests_per_second: Optional[float] = None, burst_size: int = 1):
    """
    Decorator to add rate limiting to async functions.
    
    Args:
        requests_per_second: Maximum requests per second (None for no limit)
        burst_size: Number of requests allowed in burst
    """
    def decorator(func: Callable) -> Callable:
        last_request_time = 0
        request_count = 0
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal last_request_time, request_count
            
            # If no rate limiting, just call the function
            if requests_per_second is None:
                return await func(*args, **kwargs)
            
            current_time = time.time()
            time_since_last_request = current_time - last_request_time
            min_interval = 1.0 / requests_per_second
            
            # Reset burst counter if enough time has passed
            if time_since_last_request >= min_interval:
                request_count = 0
            
            # Check if we need to wait
            if request_count >= burst_size:
                sleep_time = min_interval - time_since_last_request
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                request_count = 0
            
            request_count += 1
            last_request_time = time.time()
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def log_request_response(func=None, *, log_level: str = "INFO", enable_logging: bool = True):
    """
    Decorator to log request and response details.
    
    Args:
        func: Function to decorate (when used without parameters)
        log_level: Logging level for the messages
        enable_logging: Whether to enable logging
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not enable_logging:
                return func(*args, **kwargs)
            
            func_name = func.__name__
            getattr(logger, log_level.lower())(f"Making request: {func_name}")
            
            try:
                result = func(*args, **kwargs)
                
                if hasattr(result, 'status_code'):
                    getattr(logger, log_level.lower())(f"Response: {result.status_code} - {result.reason_phrase}")
                else:
                    getattr(logger, log_level.lower())(f"Response: {result}")
                
                return result
                
            except Exception as e:
                logger.error(f"Request failed: {type(e).__name__}: {e}")
                raise
        
        return wrapper
    
    if func is None:
        return decorator
    else:
        return decorator(func)


def async_log_request_response(func=None, *, log_level: str = "INFO", enable_logging: bool = True):
    """
    Decorator to log request and response details for async functions.
    
    Args:
        func: Function to decorate (when used without parameters)
        log_level: Logging level for the messages
        enable_logging: Whether to enable logging
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not enable_logging:
                return await func(*args, **kwargs)
            
            func_name = func.__name__
            getattr(logger, log_level.lower())(f"Making async request: {func_name}")
            
            try:
                result = await func(*args, **kwargs)
                
                if hasattr(result, 'status_code'):
                    getattr(logger, log_level.lower())(f"Response: {result.status_code} - {result.reason_phrase}")
                else:
                    getattr(logger, log_level.lower())(f"Response: {result}")
                
                return result
                
            except Exception as e:
                logger.error(f"Async request failed: {type(e).__name__}: {e}")
                raise
        
        return wrapper
    
    if func is None:
        return decorator
    else:
        return decorator(func)
