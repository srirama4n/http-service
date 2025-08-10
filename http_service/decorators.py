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
                    
                    if retry_on_exceptions:
                        should_retry = any(isinstance(e, exc_type) for exc_type in retry_on_exceptions)
                    
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
                    
                    if retry_on_exceptions:
                        should_retry = any(isinstance(e, exc_type) for exc_type in retry_on_exceptions)
                    
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


def rate_limit(requests_per_second: float):
    """
    Decorator to add rate limiting to functions.
    
    Args:
        requests_per_second: Maximum requests per second
    """
    def decorator(func: Callable) -> Callable:
        last_request_time = 0
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal last_request_time
            
            current_time = time.time()
            time_since_last_request = current_time - last_request_time
            min_interval = 1.0 / requests_per_second
            
            if time_since_last_request < min_interval:
                sleep_time = min_interval - time_since_last_request
                time.sleep(sleep_time)
            
            last_request_time = time.time()
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def async_rate_limit(requests_per_second: float):
    """
    Decorator to add rate limiting to async functions.
    
    Args:
        requests_per_second: Maximum requests per second
    """
    def decorator(func: Callable) -> Callable:
        last_request_time = 0
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal last_request_time
            
            current_time = time.time()
            time_since_last_request = current_time - last_request_time
            min_interval = 1.0 / requests_per_second
            
            if time_since_last_request < min_interval:
                sleep_time = min_interval - time_since_last_request
                await asyncio.sleep(sleep_time)
            
            last_request_time = time.time()
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def log_request_response(log_level: str = "INFO"):
    """
    Decorator to log request and response details.
    
    Args:
        log_level: Logging level for the messages
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            logger.log(getattr(logging, log_level.upper()), f"Making request: {func_name}")
            
            try:
                result = func(*args, **kwargs)
                
                if hasattr(result, 'status_code'):
                    logger.log(getattr(logging, log_level.upper()), 
                             f"Response: {result.status_code} - {result.reason_phrase}")
                
                return result
                
            except Exception as e:
                logger.error(f"Request failed: {type(e).__name__}: {e}")
                raise
        
        return wrapper
    return decorator


def async_log_request_response(log_level: str = "INFO"):
    """
    Decorator to log request and response details for async functions.
    
    Args:
        log_level: Logging level for the messages
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            func_name = func.__name__
            logger.log(getattr(logging, log_level.upper()), f"Making async request: {func_name}")
            
            try:
                result = await func(*args, **kwargs)
                
                if hasattr(result, 'status_code'):
                    logger.log(getattr(logging, log_level.upper()), 
                             f"Response: {result.status_code} - {result.reason_phrase}")
                
                return result
                
            except Exception as e:
                logger.error(f"Async request failed: {type(e).__name__}: {e}")
                raise
        
        return wrapper
    return decorator
