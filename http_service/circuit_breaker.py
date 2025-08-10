"""
Circuit Breaker implementation for HTTP client.
Provides fault tolerance by preventing cascading failures.
"""

import time
import logging
import threading
from typing import Optional, Callable, Any, Dict
from enum import Enum
from .models import CircuitBreakerState, CircuitBreakerConfig
import httpx

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """
    Circuit Breaker implementation for fault tolerance.
    
    The circuit breaker has three states:
    - CLOSED: Normal operation, requests are allowed
    - OPEN: Failing, requests are rejected immediately
    - HALF_OPEN: Testing if service has recovered
    """
    
    def __init__(self, config: CircuitBreakerConfig):
        """
        Initialize circuit breaker.
        
        Args:
            config: Circuit breaker configuration
        """
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self.last_success_time = 0
        self._lock = threading.RLock()
        
        # Statistics
        self.total_requests = 0
        self.total_failures = 0
        self.total_successes = 0
        self.total_rejected = 0
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
        
        Returns:
            Function result
        
        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: Original exception from function
        """
        if not self.config.enabled:
            return func(*args, **kwargs)
        
        with self._lock:
            self.total_requests += 1
            
            # Check if circuit is open
            if self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self._set_half_open()
                else:
                    self.total_rejected += 1
                    logger.warning(f"Circuit breaker is OPEN, rejecting request")
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker is OPEN. Last failure: {self.last_failure_time}"
                    )
            
            # Execute function
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
                
            except Exception as e:
                self._on_failure(e)
                raise
    
    async def acall(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute async function with circuit breaker protection.
        
        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
        
        Returns:
            Function result
        
        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: Original exception from function
        """
        if not self.config.enabled:
            return await func(*args, **kwargs)
        
        with self._lock:
            self.total_requests += 1
            
            # Check if circuit is open
            if self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self._set_half_open()
                else:
                    self.total_rejected += 1
                    logger.warning(f"Circuit breaker is OPEN, rejecting async request")
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker is OPEN. Last failure: {self.last_failure_time}"
                    )
            
            # Execute function
            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
                
            except Exception as e:
                self._on_failure(e)
                raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        return time.time() - self.last_failure_time >= self.config.recovery_timeout
    
    def _set_half_open(self):
        """Set circuit to half-open state."""
        self.state = CircuitBreakerState.HALF_OPEN
        self.success_count = 0
        logger.info("Circuit breaker set to HALF_OPEN")
    
    def _on_success(self):
        """Handle successful execution."""
        with self._lock:
            self.last_success_time = time.time()
            self.total_successes += 1
            
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self._set_closed()
            else:
                # Reset failure count on success
                self.failure_count = 0
    
    def _on_failure(self, exception: Exception):
        """Handle failed execution."""
        with self._lock:
            self.last_failure_time = time.time()
            self.total_failures += 1
            self.failure_count += 1
            
            logger.warning(f"Circuit breaker failure: {type(exception).__name__}: {exception}")
            
            if self.state == CircuitBreakerState.HALF_OPEN:
                # Back to open state
                self._set_open()
            elif self.state == CircuitBreakerState.CLOSED:
                if self.failure_count >= self.config.failure_threshold:
                    self._set_open()
    
    def _set_closed(self):
        """Set circuit to closed state."""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        logger.info("Circuit breaker set to CLOSED")
    
    def _set_open(self):
        """Set circuit to open state."""
        self.state = CircuitBreakerState.OPEN
        logger.warning(f"Circuit breaker set to OPEN after {self.failure_count} failures")
    
    def is_open(self) -> bool:
        """Check if circuit is open."""
        return self.state == CircuitBreakerState.OPEN
    
    def is_closed(self) -> bool:
        """Check if circuit is closed."""
        return self.state == CircuitBreakerState.CLOSED
    
    def is_half_open(self) -> bool:
        """Check if circuit is half-open."""
        return self.state == CircuitBreakerState.HALF_OPEN
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure_time': self.last_failure_time,
            'last_success_time': self.last_success_time,
            'total_requests': self.total_requests,
            'total_failures': self.total_failures,
            'total_successes': self.total_successes,
            'total_rejected': self.total_rejected,
            'failure_rate': self.total_failures / max(self.total_requests, 1),
            'success_rate': self.total_successes / max(self.total_requests, 1)
        }
    
    def reset(self):
        """Manually reset circuit breaker to closed state."""
        with self._lock:
            self._set_closed()
            logger.info("Circuit breaker manually reset to CLOSED")
    
    def force_open(self):
        """Manually force circuit breaker to open state."""
        with self._lock:
            self._set_open()
            logger.info("Circuit breaker manually forced to OPEN")


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass


def circuit_breaker_decorator(config: CircuitBreakerConfig):
    """
    Decorator to add circuit breaker functionality to functions.
    
    Args:
        config: Circuit breaker configuration
    
    Returns:
        Decorated function
    """
    breaker = CircuitBreaker(config)
    
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator


def async_circuit_breaker_decorator(config: CircuitBreakerConfig):
    """
    Decorator to add circuit breaker functionality to async functions.
    
    Args:
        config: Circuit breaker configuration
    
    Returns:
        Decorated async function
    """
    breaker = CircuitBreaker(config)
    
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            return await breaker.acall(func, *args, **kwargs)
        return wrapper
    return decorator


def should_trigger_circuit_breaker(response: Optional[httpx.Response], 
                                 exception: Optional[Exception],
                                 config: CircuitBreakerConfig) -> bool:
    """
    Determine if a response or exception should trigger circuit breaker.
    
    Args:
        response: HTTP response (if available)
        exception: Exception (if available)
        config: Circuit breaker configuration
    
    Returns:
        True if circuit breaker should be triggered
    """
    # Check for timeout exceptions
    if exception and any(isinstance(exception, exc_type) for exc_type in config.timeout_exceptions):
        return True
    
    # Check for expected exceptions
    if exception and isinstance(exception, config.expected_exception):
        return True
    
    # Check for failure status codes
    if response and response.status_code in config.failure_status_codes:
        return True
    
    return False
