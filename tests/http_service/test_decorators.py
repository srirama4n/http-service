"""
Unit tests for the decorators module.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch
from http_service.patterns.decorators import (
    retry, async_retry, rate_limit, async_rate_limit,
    log_request_response, async_log_request_response
)


class TestRetryDecorator:
    """Test retry decorator."""
    
    def test_retry_success_on_first_try(self):
        """Test retry decorator with success on first try."""
        call_count = 0
        
        @retry(max_retries=3, retry_delay=0.1)
        def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = successful_function()
        
        assert result == "success"
        assert call_count == 1
    
    def test_retry_success_after_failures(self):
        """Test retry decorator with success after some failures."""
        call_count = 0
        
        @retry(max_retries=3, retry_delay=0.1)
        def eventually_successful_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("temporary error")
            return "success"
        
        result = eventually_successful_function()
        
        assert result == "success"
        assert call_count == 3
    
    def test_retry_max_retries_exceeded(self):
        """Test retry decorator with max retries exceeded."""
        call_count = 0
        
        @retry(max_retries=2, retry_delay=0.1)
        def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("permanent error")
        
        with pytest.raises(ValueError, match="permanent error"):
            always_failing_function()
        
        assert call_count == 3  # Initial call + 2 retries
    
    def test_retry_with_backoff(self):
        """Test retry decorator with exponential backoff."""
        call_count = 0
        start_time = time.time()
        
        @retry(max_retries=2, retry_delay=0.1, backoff_factor=2.0)
        def eventually_successful_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("temporary error")
            return "success"
        
        result = eventually_successful_function()
        
        assert result == "success"
        assert call_count == 3
        
        # Check that backoff was applied (should take longer than simple retry)
        elapsed_time = time.time() - start_time
        assert elapsed_time > 0.3  # 0.1 + 0.2 = 0.3 seconds minimum
    
    def test_retry_with_status_codes(self):
        """Test retry decorator with specific status codes."""
        call_count = 0
        
        @retry(max_retries=2, retry_delay=0.1, retry_on_status_codes=[500, 502])
        def function_with_status_code():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                response = Mock()
                response.status_code = 500
                raise Exception("HTTP 500")
            return "success"
        
        result = function_with_status_code()
        
        assert result == "success"
        assert call_count == 3
    
    def test_retry_with_exceptions(self):
        """Test retry decorator with specific exceptions."""
        call_count = 0
        
        @retry(max_retries=2, retry_delay=0.1, retry_on_exceptions=[ValueError])
        def function_with_exception():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("temporary error")
            return "success"
        
        result = function_with_exception()
        
        assert result == "success"
        assert call_count == 3
    
    def test_retry_with_non_retryable_exception(self):
        """Test retry decorator with non-retryable exception."""
        call_count = 0
        
        @retry(max_retries=3, retry_delay=0.1, retry_on_exceptions=[ValueError])
        def function_with_type_error():
            nonlocal call_count
            call_count += 1
            raise TypeError("type error")
        
        with pytest.raises(TypeError, match="type error"):
            function_with_type_error()
        
        assert call_count == 1  # Should not retry


class TestAsyncRetryDecorator:
    """Test async_retry decorator."""
    
    @pytest.mark.asyncio
    async def test_async_retry_success_on_first_try(self):
        """Test async_retry decorator with success on first try."""
        call_count = 0
        
        @async_retry(max_retries=3, retry_delay=0.1)
        async def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await successful_function()
        
        assert result == "success"
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_async_retry_success_after_failures(self):
        """Test async_retry decorator with success after some failures."""
        call_count = 0
        
        @async_retry(max_retries=3, retry_delay=0.1)
        async def eventually_successful_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("temporary error")
            return "success"
        
        result = await eventually_successful_function()
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_async_retry_max_retries_exceeded(self):
        """Test async_retry decorator with max retries exceeded."""
        call_count = 0
        
        @async_retry(max_retries=2, retry_delay=0.1)
        async def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("permanent error")
        
        with pytest.raises(ValueError, match="permanent error"):
            await always_failing_function()
        
        assert call_count == 3  # Initial call + 2 retries
    
    @pytest.mark.asyncio
    async def test_async_retry_with_backoff(self):
        """Test async_retry decorator with exponential backoff."""
        call_count = 0
        start_time = time.time()
        
        @async_retry(max_retries=2, retry_delay=0.1, backoff_factor=2.0)
        async def eventually_successful_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("temporary error")
            return "success"
        
        result = await eventually_successful_function()
        
        assert result == "success"
        assert call_count == 3
        
        # Check that backoff was applied
        elapsed_time = time.time() - start_time
        assert elapsed_time > 0.3  # 0.1 + 0.2 = 0.3 seconds minimum


class TestRateLimitDecorator:
    """Test rate_limit decorator."""
    
    def test_rate_limit_basic(self):
        """Test rate_limit decorator with basic rate limiting."""
        call_count = 0
        
        @rate_limit(requests_per_second=2)
        def test_function():
            nonlocal call_count
            call_count += 1
            return f"call_{call_count}"
        
        # First two calls should be immediate
        result1 = test_function()
        result2 = test_function()
        
        assert result1 == "call_1"
        assert result2 == "call_2"
        assert call_count == 2
        
        # Third call should be rate limited
        start_time = time.time()
        result3 = test_function()
        elapsed_time = time.time() - start_time
        
        assert result3 == "call_3"
        assert call_count == 3
        assert elapsed_time >= 0.5  # Should be rate limited
    
    def test_rate_limit_burst(self):
        """Test rate_limit decorator with burst size."""
        call_count = 0
        
        @rate_limit(requests_per_second=1, burst_size=3)
        def test_function():
            nonlocal call_count
            call_count += 1
            return f"call_{call_count}"
        
        # First three calls should be immediate (burst)
        results = []
        for i in range(3):
            results.append(test_function())
        
        assert results == ["call_1", "call_2", "call_3"]
        assert call_count == 3
        
        # Fourth call should be rate limited
        start_time = time.time()
        result4 = test_function()
        elapsed_time = time.time() - start_time
        
        assert result4 == "call_4"
        assert call_count == 4
        assert elapsed_time >= 1.0  # Should be rate limited
    
    def test_rate_limit_no_limit(self):
        """Test rate_limit decorator with no rate limiting."""
        call_count = 0
        
        @rate_limit(requests_per_second=None)
        def test_function():
            nonlocal call_count
            call_count += 1
            return f"call_{call_count}"
        
        # All calls should be immediate
        start_time = time.time()
        for i in range(5):
            test_function()
        elapsed_time = time.time() - start_time
        
        assert call_count == 5
        assert elapsed_time < 0.1  # Should be very fast


class TestAsyncRateLimitDecorator:
    """Test async_rate_limit decorator."""
    
    @pytest.mark.asyncio
    async def test_async_rate_limit_basic(self):
        """Test async_rate_limit decorator with basic rate limiting."""
        call_count = 0
        
        @async_rate_limit(requests_per_second=2)
        async def test_function():
            nonlocal call_count
            call_count += 1
            return f"call_{call_count}"
        
        # First two calls should be immediate
        result1 = await test_function()
        result2 = await test_function()
        
        assert result1 == "call_1"
        assert result2 == "call_2"
        assert call_count == 2
        
        # Third call should be rate limited
        start_time = time.time()
        result3 = await test_function()
        elapsed_time = time.time() - start_time
        
        assert result3 == "call_3"
        assert call_count == 3
        assert elapsed_time >= 0.5  # Should be rate limited
    
    @pytest.mark.asyncio
    async def test_async_rate_limit_burst(self):
        """Test async_rate_limit decorator with burst size."""
        call_count = 0
        
        @async_rate_limit(requests_per_second=1, burst_size=3)
        async def test_function():
            nonlocal call_count
            call_count += 1
            return f"call_{call_count}"
        
        # First three calls should be immediate (burst)
        results = []
        for i in range(3):
            results.append(await test_function())
        
        assert results == ["call_1", "call_2", "call_3"]
        assert call_count == 3
        
        # Fourth call should be rate limited
        start_time = time.time()
        result4 = await test_function()
        elapsed_time = time.time() - start_time
        
        assert result4 == "call_4"
        assert call_count == 4
        assert elapsed_time >= 1.0  # Should be rate limited


class TestLogRequestResponseDecorator:
    """Test log_request_response decorator."""
    
    @patch('http_service.patterns.decorators.logger')
    def test_log_request_response_success(self, mock_logger):
        """Test log_request_response decorator with successful request."""
        @log_request_response
        def test_function():
            return "success"
        
        result = test_function()
        
        assert result == "success"
        # Should log request and response
        assert mock_logger.info.call_count >= 2
    
    @patch('http_service.patterns.decorators.logger')
    def test_log_request_response_exception(self, mock_logger):
        """Test log_request_response decorator with exception."""
        @log_request_response
        def test_function():
            raise ValueError("test error")
        
        with pytest.raises(ValueError, match="test error"):
            test_function()
        
        # Should log request and error
        assert mock_logger.info.call_count >= 1
        assert mock_logger.error.call_count >= 1
    
    @patch('http_service.patterns.decorators.logger')
    def test_log_request_response_disabled(self, mock_logger):
        """Test log_request_response decorator when logging is disabled."""
        @log_request_response(enable_logging=False)
        def test_function():
            return "success"
        
        result = test_function()
        
        assert result == "success"
        # Should not log anything
        mock_logger.info.assert_not_called()
        mock_logger.error.assert_not_called()


class TestAsyncLogRequestResponseDecorator:
    """Test async_log_request_response decorator."""
    
    @pytest.mark.asyncio
    @patch('http_service.patterns.decorators.logger')
    async def test_async_log_request_response_success(self, mock_logger):
        """Test async_log_request_response decorator with successful request."""
        @async_log_request_response
        async def test_function():
            return "success"
        
        result = await test_function()
        
        assert result == "success"
        # Should log request and response
        assert mock_logger.info.call_count >= 2
    
    @pytest.mark.asyncio
    @patch('http_service.patterns.decorators.logger')
    async def test_async_log_request_response_exception(self, mock_logger):
        """Test async_log_request_response decorator with exception."""
        @async_log_request_response
        async def test_function():
            raise ValueError("test error")
        
        with pytest.raises(ValueError, match="test error"):
            await test_function()
        
        # Should log request and error
        assert mock_logger.info.call_count >= 1
        assert mock_logger.error.call_count >= 1
    
    @pytest.mark.asyncio
    @patch('http_service.patterns.decorators.logger')
    async def test_async_log_request_response_disabled(self, mock_logger):
        """Test async_log_request_response decorator when logging is disabled."""
        @async_log_request_response(enable_logging=False)
        async def test_function():
            return "success"
        
        result = await test_function()
        
        assert result == "success"
        # Should not log anything
        mock_logger.info.assert_not_called()
        mock_logger.error.assert_not_called()


class TestDecoratorCombinations:
    """Test combinations of decorators."""
    
    def test_retry_and_rate_limit(self):
        """Test combining retry and rate_limit decorators."""
        call_count = 0
        
        @retry(max_retries=2, retry_delay=0.1)
        @rate_limit(requests_per_second=5)
        def test_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("temporary error")
            return "success"
        
        result = test_function()
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_async_retry_and_rate_limit(self):
        """Test combining async_retry and async_rate_limit decorators."""
        call_count = 0
        
        @async_retry(max_retries=2, retry_delay=0.1)
        @async_rate_limit(requests_per_second=5)
        async def test_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("temporary error")
            return "success"
        
        result = await test_function()
        
        assert result == "success"
        assert call_count == 3
    
    @patch('http_service.patterns.decorators.logger')
    def test_retry_and_logging(self, mock_logger):
        """Test combining retry and logging decorators."""
        call_count = 0
        
        @retry(max_retries=2, retry_delay=0.1)
        @log_request_response
        def test_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("temporary error")
            return "success"
        
        result = test_function()
        
        assert result == "success"
        assert call_count == 3
        # Should log each attempt
        assert mock_logger.info.call_count >= 3
