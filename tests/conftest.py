"""
Pytest configuration and fixtures for HTTP client tests.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from typing import Dict, Any

from http_service.models import (
    RetryConfig, TimeoutConfig, AuthConfig, CircuitBreakerConfig,
    ConnectionPoolConfig, RateLimitConfig, LoggingConfig
)
from http_service.config import HTTPClientConfig


@pytest.fixture
def sample_retry_config():
    """Sample retry configuration for testing."""
    return RetryConfig(
        max_retries=3,
        retry_delay=1.0,
        backoff_factor=2.0,
        retry_on_status_codes=[429, 500, 502, 503, 504]
    )


@pytest.fixture
def sample_timeout_config():
    """Sample timeout configuration for testing."""
    return TimeoutConfig(
        connect_timeout=10.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=10.0
    )


@pytest.fixture
def sample_auth_config():
    """Sample authentication configuration for testing."""
    return AuthConfig(
        auth_type="api_key",
        api_key="test-api-key",
        api_key_header="X-API-Key"
    )


@pytest.fixture
def sample_circuit_breaker_config():
    """Sample circuit breaker configuration for testing."""
    return CircuitBreakerConfig(
        enabled=True,
        failure_threshold=3,
        recovery_timeout=10.0,
        failure_status_codes=[500, 502, 503, 504],
        success_threshold=2
    )


@pytest.fixture
def sample_http_client_config():
    """Sample HTTP client configuration for testing."""
    return HTTPClientConfig(
        base_url="https://api.example.com",
        verify_ssl=True,
        enable_logging=True,
        connect_timeout=10.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=10.0,
        max_connections=10,
        max_keepalive_connections=5,
        keepalive_expiry=30.0,
        max_retries=3,
        retry_delay=1.0,
        backoff_factor=2.0,
        retry_on_status_codes=[429, 500, 502, 503, 504],
        rate_limit_requests_per_second=10.0,
        circuit_breaker_enabled=True,
        circuit_breaker_failure_threshold=3,
        circuit_breaker_recovery_timeout=10.0,
        circuit_breaker_failure_status_codes=[500, 502, 503, 504],
        circuit_breaker_success_threshold=2,
        auth_type="api_key",
        api_key="test-api-key",
        api_key_header="X-API-Key",
        custom_headers={"X-Test-Header": "test-value"}
    )


@pytest.fixture
def mock_response():
    """Mock HTTP response for testing."""
    response = Mock()
    response.status_code = 200
    response.reason_phrase = "OK"
    response.headers = {"content-type": "application/json"}
    response.json.return_value = {"message": "success"}
    response.text = '{"message": "success"}'
    response.content = b'{"message": "success"}'
    return response


@pytest.fixture
def mock_error_response():
    """Mock error HTTP response for testing."""
    response = Mock()
    response.status_code = 500
    response.reason_phrase = "Internal Server Error"
    response.headers = {"content-type": "application/json"}
    response.json.return_value = {"error": "server error"}
    response.text = '{"error": "server error"}'
    response.content = b'{"error": "server error"}'
    return response


@pytest.fixture
def mock_httpx_client():
    """Mock HTTPX client for testing."""
    client = Mock()
    client.get.return_value = mock_response()
    client.post.return_value = mock_response()
    client.put.return_value = mock_response()
    client.patch.return_value = mock_response()
    client.delete.return_value = mock_response()
    client.request.return_value = mock_response()
    return client


@pytest.fixture
def mock_async_httpx_client():
    """Mock async HTTPX client for testing."""
    client = Mock()
    client.get = Mock(return_value=asyncio.Future())
    client.get.return_value.set_result(mock_response())
    client.post = Mock(return_value=asyncio.Future())
    client.post.return_value.set_result(mock_response())
    client.put = Mock(return_value=asyncio.Future())
    client.put.return_value.set_result(mock_response())
    client.patch = Mock(return_value=asyncio.Future())
    client.patch.return_value.set_result(mock_response())
    client.delete = Mock(return_value=asyncio.Future())
    client.delete.return_value.set_result(mock_response())
    client.request = Mock(return_value=asyncio.Future())
    client.request.return_value.set_result(mock_response())
    return client


@pytest.fixture
def sample_headers():
    """Sample headers for testing."""
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer test-token",
        "X-API-Key": "test-api-key",
        "User-Agent": "TestClient/1.0"
    }


@pytest.fixture
def sample_data():
    """Sample data for testing."""
    return {
        "id": 1,
        "name": "Test Item",
        "description": "A test item for testing",
        "active": True,
        "tags": ["test", "example"]
    }


@pytest.fixture
def sample_urls():
    """Sample URLs for testing."""
    return {
        "base": "https://api.example.com",
        "users": "https://api.example.com/users",
        "posts": "https://api.example.com/posts",
        "relative": "/api/v1/users",
        "with_params": "https://api.example.com/users?page=1&limit=10"
    }


@pytest.fixture
def sample_exceptions():
    """Sample exceptions for testing."""
    import httpx
    
    return {
        "connect_timeout": httpx.ConnectTimeout("Connection timeout"),
        "read_timeout": httpx.ReadTimeout("Read timeout"),
        "write_timeout": httpx.WriteTimeout("Write timeout"),
        "pool_timeout": httpx.PoolTimeout("Pool timeout"),
        "http_status_error": httpx.HTTPStatusError("HTTP 500", request=Mock(), response=mock_error_response()),
        "connect_error": httpx.ConnectError("Connection error"),
        "remote_protocol_error": httpx.RemoteProtocolError("Remote protocol error")
    }


def mock_response():
    """Helper function to create a mock response."""
    response = Mock()
    response.status_code = 200
    response.reason_phrase = "OK"
    response.headers = {"content-type": "application/json"}
    response.json.return_value = {"message": "success"}
    response.text = '{"message": "success"}'
    response.content = b'{"message": "success"}'
    return response


def mock_error_response():
    """Helper function to create a mock error response."""
    response = Mock()
    response.status_code = 500
    response.reason_phrase = "Internal Server Error"
    response.headers = {"content-type": "application/json"}
    response.json.return_value = {"error": "server error"}
    response.text = '{"error": "server error"}'
    response.content = b'{"error": "server error"}'
    return response


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
