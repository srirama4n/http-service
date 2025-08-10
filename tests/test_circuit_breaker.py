"""
Unit tests for the circuit breaker module.
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch
from http_service.circuit_breaker import (
    CircuitBreaker, CircuitBreakerOpenError, CircuitBreakerHalfOpenError,
    should_trigger_circuit_breaker
)
from http_service.models import CircuitBreakerState, CircuitBreakerConfig


class TestCircuitBreaker:
    """Test CircuitBreaker class."""
    
    def test_circuit_breaker_initial_state(self):
        """Test CircuitBreaker initial state."""
        config = CircuitBreakerConfig(
            enabled=True,
            failure_threshold=3,
            recovery_timeout=10.0,
            success_threshold=2
        )
        breaker = CircuitBreaker(config)
        
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.failure_count == 0
        assert breaker.success_count == 0
        assert breaker.last_failure_time is None
    
    def test_circuit_breaker_disabled(self):
        """Test CircuitBreaker when disabled."""
        config = CircuitBreakerConfig(enabled=False)
        breaker = CircuitBreaker(config)
        
        # Should always allow calls when disabled
        result = breaker.call(lambda: "success")
        assert result == "success"
        assert breaker.state == CircuitBreakerState.CLOSED
    
    def test_circuit_breaker_successful_call(self):
        """Test CircuitBreaker with successful call."""
        config = CircuitBreakerConfig(enabled=True, failure_threshold=3)
        breaker = CircuitBreaker(config)
        
        result = breaker.call(lambda: "success")
        
        assert result == "success"
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.failure_count == 0
        assert breaker.success_count == 0  # Success count only matters in HALF_OPEN state
    
    def test_circuit_breaker_failure_call(self):
        """Test CircuitBreaker with failure call."""
        config = CircuitBreakerConfig(enabled=True, failure_threshold=3)
        breaker = CircuitBreaker(config)
        
        def failing_function():
            raise ValueError("test error")
        
        with pytest.raises(ValueError):
            breaker.call(failing_function)
        
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.failure_count == 1
        assert breaker.last_failure_time is not None
    
    def test_circuit_breaker_open_on_threshold(self):
        """Test CircuitBreaker opens when failure threshold is reached."""
        config = CircuitBreakerConfig(enabled=True, failure_threshold=2)
        breaker = CircuitBreaker(config)
        
        def failing_function():
            raise ValueError("test error")
        
        # First failure
        with pytest.raises(ValueError):
            breaker.call(failing_function)
        
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.failure_count == 1
        
        # Second failure - should open circuit
        with pytest.raises(ValueError):
            breaker.call(failing_function)
        
        assert breaker.state == CircuitBreakerState.OPEN
        assert breaker.failure_count == 2
    
    def test_circuit_breaker_open_blocks_calls(self):
        """Test CircuitBreaker blocks calls when open."""
        config = CircuitBreakerConfig(enabled=True, failure_threshold=1)
        breaker = CircuitBreaker(config)
        
        def failing_function():
            raise ValueError("test error")
        
        # Trigger circuit to open
        with pytest.raises(ValueError):
            breaker.call(failing_function)
        
        assert breaker.state == CircuitBreakerState.OPEN
        
        # Should block subsequent calls
        with pytest.raises(CircuitBreakerOpenError):
            breaker.call(lambda: "success")
    
    def test_circuit_breaker_half_open_after_timeout(self):
        """Test CircuitBreaker transitions to half-open after timeout."""
        config = CircuitBreakerConfig(enabled=True, failure_threshold=1, recovery_timeout=0.1)
        breaker = CircuitBreaker(config)
        
        def failing_function():
            raise ValueError("test error")
        
        # Trigger circuit to open
        with pytest.raises(ValueError):
            breaker.call(failing_function)
        
        assert breaker.state == CircuitBreakerState.OPEN
        
        # Wait for timeout
        time.sleep(0.2)
        
        # Should transition to half-open
        assert breaker.state == CircuitBreakerState.HALF_OPEN
    
    def test_circuit_breaker_half_open_success(self):
        """Test CircuitBreaker closes on success in half-open state."""
        config = CircuitBreakerConfig(
            enabled=True, 
            failure_threshold=1, 
            recovery_timeout=0.1,
            success_threshold=1
        )
        breaker = CircuitBreaker(config)
        
        def failing_function():
            raise ValueError("test error")
        
        # Trigger circuit to open
        with pytest.raises(ValueError):
            breaker.call(failing_function)
        
        # Wait for timeout
        time.sleep(0.2)
        
        # Success in half-open state
        result = breaker.call(lambda: "success")
        
        assert result == "success"
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.failure_count == 0
        assert breaker.success_count == 0
    
    def test_circuit_breaker_half_open_failure(self):
        """Test CircuitBreaker opens again on failure in half-open state."""
        config = CircuitBreakerConfig(
            enabled=True, 
            failure_threshold=1, 
            recovery_timeout=0.1,
            success_threshold=2
        )
        breaker = CircuitBreaker(config)
        
        def failing_function():
            raise ValueError("test error")
        
        # Trigger circuit to open
        with pytest.raises(ValueError):
            breaker.call(failing_function)
        
        # Wait for timeout
        time.sleep(0.2)
        
        # Failure in half-open state
        with pytest.raises(ValueError):
            breaker.call(failing_function)
        
        assert breaker.state == CircuitBreakerState.OPEN
        assert breaker.failure_count == 2
    
    def test_circuit_breaker_half_open_success_threshold(self):
        """Test CircuitBreaker requires multiple successes to close."""
        config = CircuitBreakerConfig(
            enabled=True, 
            failure_threshold=1, 
            recovery_timeout=0.1,
            success_threshold=2
        )
        breaker = CircuitBreaker(config)
        
        def failing_function():
            raise ValueError("test error")
        
        # Trigger circuit to open
        with pytest.raises(ValueError):
            breaker.call(failing_function)
        
        # Wait for timeout
        time.sleep(0.2)
        
        # First success - should stay in half-open
        result = breaker.call(lambda: "success")
        assert result == "success"
        assert breaker.state == CircuitBreakerState.HALF_OPEN
        assert breaker.success_count == 1
        
        # Second success - should close
        result = breaker.call(lambda: "success")
        assert result == "success"
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.success_count == 0  # Reset after closing
    
    def test_circuit_breaker_async_call(self):
        """Test CircuitBreaker async call method."""
        config = CircuitBreakerConfig(enabled=True, failure_threshold=3)
        breaker = CircuitBreaker(config)
        
        async def async_function():
            return "success"
        
        import asyncio
        result = asyncio.run(breaker.acall(async_function))
        
        assert result == "success"
        assert breaker.state == CircuitBreakerState.CLOSED
    
    def test_circuit_breaker_async_failure(self):
        """Test CircuitBreaker async call with failure."""
        config = CircuitBreakerConfig(enabled=True, failure_threshold=1)
        breaker = CircuitBreaker(config)
        
        async def async_failing_function():
            raise ValueError("test error")
        
        import asyncio
        with pytest.raises(ValueError):
            asyncio.run(breaker.acall(async_failing_function))
        
        assert breaker.state == CircuitBreakerState.OPEN
    
    def test_circuit_breaker_thread_safety(self):
        """Test CircuitBreaker thread safety."""
        config = CircuitBreakerConfig(enabled=True, failure_threshold=5)
        breaker = CircuitBreaker(config)
        
        def failing_function():
            raise ValueError("test error")
        
        def call_breaker():
            try:
                breaker.call(failing_function)
            except (ValueError, CircuitBreakerOpenError):
                pass
        
        # Create multiple threads calling the breaker
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=call_breaker)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should be in a consistent state
        assert breaker.state in [CircuitBreakerState.CLOSED, CircuitBreakerState.OPEN]
    
    def test_circuit_breaker_reset(self):
        """Test CircuitBreaker reset method."""
        config = CircuitBreakerConfig(enabled=True, failure_threshold=1)
        breaker = CircuitBreaker(config)
        
        def failing_function():
            raise ValueError("test error")
        
        # Trigger circuit to open
        with pytest.raises(ValueError):
            breaker.call(failing_function)
        
        assert breaker.state == CircuitBreakerState.OPEN
        
        # Reset circuit
        breaker.reset()
        
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.failure_count == 0
        assert breaker.success_count == 0
        assert breaker.last_failure_time is None
    
    def test_circuit_breaker_force_open(self):
        """Test CircuitBreaker force_open method."""
        config = CircuitBreakerConfig(enabled=True, failure_threshold=10)
        breaker = CircuitBreaker(config)
        
        assert breaker.state == CircuitBreakerState.CLOSED
        
        breaker.force_open()
        
        assert breaker.state == CircuitBreakerState.OPEN
    
    def test_circuit_breaker_get_stats(self):
        """Test CircuitBreaker get_stats method."""
        config = CircuitBreakerConfig(enabled=True, failure_threshold=3)
        breaker = CircuitBreaker(config)
        
        stats = breaker.get_stats()
        
        assert "state" in stats
        assert "failure_count" in stats
        assert "success_count" in stats
        assert "last_failure_time" in stats
        assert "total_calls" in stats
        assert "successful_calls" in stats
        assert "failed_calls" in stats
        assert "success_rate" in stats
    
    def test_circuit_breaker_custom_exception_types(self):
        """Test CircuitBreaker with custom exception types."""
        config = CircuitBreakerConfig(
            enabled=True,
            failure_threshold=1,
            expected_exception=ValueError
        )
        breaker = CircuitBreaker(config)
        
        def failing_function():
            raise ValueError("test error")
        
        # Should count as failure
        with pytest.raises(ValueError):
            breaker.call(failing_function)
        
        assert breaker.state == CircuitBreakerState.OPEN
        
        def other_error_function():
            raise TypeError("other error")
        
        # Should not count as failure for circuit breaker
        with pytest.raises(TypeError):
            breaker.call(other_error_function)
        
        # Should still be open
        assert breaker.state == CircuitBreakerState.OPEN


class TestShouldTriggerCircuitBreaker:
    """Test should_trigger_circuit_breaker function."""
    
    def test_should_trigger_circuit_breaker_status_code(self):
        """Test should_trigger_circuit_breaker with status code."""
        response = Mock()
        response.status_code = 500
        
        config = CircuitBreakerConfig(
            enabled=True,
            failure_status_codes=[500, 502, 503, 504]
        )
        
        assert should_trigger_circuit_breaker(response, None, config) is True
    
    def test_should_trigger_circuit_breaker_status_code_not_trigger(self):
        """Test should_trigger_circuit_breaker with non-triggering status code."""
        response = Mock()
        response.status_code = 200
        
        config = CircuitBreakerConfig(
            enabled=True,
            failure_status_codes=[500, 502, 503, 504]
        )
        
        assert should_trigger_circuit_breaker(response, None, config) is False
    
    def test_should_trigger_circuit_breaker_exception(self):
        """Test should_trigger_circuit_breaker with exception."""
        response = None
        exception = ValueError("test error")
        
        config = CircuitBreakerConfig(
            enabled=True,
            expected_exception=ValueError
        )
        
        assert should_trigger_circuit_breaker(response, exception, config) is True
    
    def test_should_trigger_circuit_breaker_exception_not_trigger(self):
        """Test should_trigger_circuit_breaker with non-triggering exception."""
        response = None
        exception = TypeError("test error")
        
        config = CircuitBreakerConfig(
            enabled=True,
            expected_exception=ValueError
        )
        
        assert should_trigger_circuit_breaker(response, exception, config) is False
    
    def test_should_trigger_circuit_breaker_disabled(self):
        """Test should_trigger_circuit_breaker when disabled."""
        response = Mock()
        response.status_code = 500
        
        config = CircuitBreakerConfig(enabled=False)
        
        assert should_trigger_circuit_breaker(response, None, config) is False
    
    def test_should_trigger_circuit_breaker_no_response_no_exception(self):
        """Test should_trigger_circuit_breaker with no response and no exception."""
        config = CircuitBreakerConfig(enabled=True)
        
        assert should_trigger_circuit_breaker(None, None, config) is False


class TestCircuitBreakerExceptions:
    """Test circuit breaker exceptions."""
    
    def test_circuit_breaker_open_error(self):
        """Test CircuitBreakerOpenError."""
        error = CircuitBreakerOpenError("Circuit breaker is open")
        assert str(error) == "Circuit breaker is open"
    
    def test_circuit_breaker_half_open_error(self):
        """Test CircuitBreakerHalfOpenError."""
        error = CircuitBreakerHalfOpenError("Circuit breaker is half-open")
        assert str(error) == "Circuit breaker is half-open"
