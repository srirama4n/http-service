"""
Unit tests for the models module.
"""

import pytest
import httpx
from http_service.models import (
    RetryConfig, TimeoutConfig, AuthConfig, CircuitBreakerConfig,
    ConnectionPoolConfig, RateLimitConfig, LoggingConfig, HTTPClientSettings,
    CircuitBreakerState
)


class TestRetryConfig:
    """Test RetryConfig class."""
    
    def test_retry_config_defaults(self):
        """Test RetryConfig default values."""
        config = RetryConfig()
        
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
        assert config.backoff_factor == 2.0
        assert config.retry_on_status_codes == [429, 500, 502, 503, 504]
        assert httpx.ConnectTimeout in config.retry_on_exceptions
        assert httpx.ReadTimeout in config.retry_on_exceptions
    
    def test_retry_config_custom_values(self):
        """Test RetryConfig with custom values."""
        config = RetryConfig(
            max_retries=5,
            retry_delay=2.0,
            backoff_factor=1.5,
            retry_on_status_codes=[500, 502]
        )
        
        assert config.max_retries == 5
        assert config.retry_delay == 2.0
        assert config.backoff_factor == 1.5
        assert config.retry_on_status_codes == [500, 502]


class TestTimeoutConfig:
    """Test TimeoutConfig class."""
    
    def test_timeout_config_defaults(self):
        """Test TimeoutConfig default values."""
        config = TimeoutConfig()
        
        assert config.connect_timeout == 10.0
        assert config.read_timeout == 30.0
        assert config.write_timeout == 30.0
        assert config.pool_timeout == 10.0
    
    def test_timeout_config_custom_values(self):
        """Test TimeoutConfig with custom values."""
        config = TimeoutConfig(
            connect_timeout=5.0,
            read_timeout=15.0,
            write_timeout=20.0,
            pool_timeout=5.0
        )
        
        assert config.connect_timeout == 5.0
        assert config.read_timeout == 15.0
        assert config.write_timeout == 20.0
        assert config.pool_timeout == 5.0


class TestAuthConfig:
    """Test AuthConfig class."""
    
    def test_auth_config_defaults(self):
        """Test AuthConfig default values."""
        config = AuthConfig()
        
        assert config.auth_type == "none"
        assert config.username is None
        assert config.password is None
        assert config.token is None
        assert config.api_key is None
        assert config.api_key_header == "X-API-Key"
    
    def test_auth_config_api_key(self):
        """Test AuthConfig with API key."""
        config = AuthConfig(
            auth_type="api_key",
            api_key="test-key",
            api_key_header="X-Custom-Key"
        )
        
        assert config.auth_type == "api_key"
        assert config.api_key == "test-key"
        assert config.api_key_header == "X-Custom-Key"
    
    def test_auth_config_basic(self):
        """Test AuthConfig with basic auth."""
        config = AuthConfig(
            auth_type="basic",
            username="testuser",
            password="testpass"
        )
        
        assert config.auth_type == "basic"
        assert config.username == "testuser"
        assert config.password == "testpass"
    
    def test_auth_config_bearer(self):
        """Test AuthConfig with bearer token."""
        config = AuthConfig(
            auth_type="bearer",
            token="test-token"
        )
        
        assert config.auth_type == "bearer"
        assert config.token == "test-token"


class TestCircuitBreakerConfig:
    """Test CircuitBreakerConfig class."""
    
    def test_circuit_breaker_config_defaults(self):
        """Test CircuitBreakerConfig default values."""
        config = CircuitBreakerConfig()
        
        assert config.enabled is False
        assert config.failure_threshold == 5
        assert config.recovery_timeout == 60.0
        assert config.expected_exception == Exception
        assert config.failure_status_codes == [500, 502, 503, 504]
        assert config.success_threshold == 2
        assert httpx.ConnectTimeout in config.timeout_exceptions
    
    def test_circuit_breaker_config_custom_values(self):
        """Test CircuitBreakerConfig with custom values."""
        config = CircuitBreakerConfig(
            enabled=True,
            failure_threshold=3,
            recovery_timeout=30.0,
            failure_status_codes=[500, 502],
            success_threshold=1
        )
        
        assert config.enabled is True
        assert config.failure_threshold == 3
        assert config.recovery_timeout == 30.0
        assert config.failure_status_codes == [500, 502]
        assert config.success_threshold == 1


class TestConnectionPoolConfig:
    """Test ConnectionPoolConfig class."""
    
    def test_connection_pool_config_defaults(self):
        """Test ConnectionPoolConfig default values."""
        config = ConnectionPoolConfig()
        
        assert config.max_connections == 10
        assert config.max_keepalive_connections == 5
        assert config.keepalive_expiry == 30.0
    
    def test_connection_pool_config_custom_values(self):
        """Test ConnectionPoolConfig with custom values."""
        config = ConnectionPoolConfig(
            max_connections=20,
            max_keepalive_connections=10,
            keepalive_expiry=60.0
        )
        
        assert config.max_connections == 20
        assert config.max_keepalive_connections == 10
        assert config.keepalive_expiry == 60.0


class TestRateLimitConfig:
    """Test RateLimitConfig class."""
    
    def test_rate_limit_config_defaults(self):
        """Test RateLimitConfig default values."""
        config = RateLimitConfig()
        
        assert config.requests_per_second is None
        assert config.burst_size is None
    
    def test_rate_limit_config_custom_values(self):
        """Test RateLimitConfig with custom values."""
        config = RateLimitConfig(
            requests_per_second=10.0,
            burst_size=5
        )
        
        assert config.requests_per_second == 10.0
        assert config.burst_size == 5


class TestLoggingConfig:
    """Test LoggingConfig class."""
    
    def test_logging_config_defaults(self):
        """Test LoggingConfig default values."""
        config = LoggingConfig()
        
        assert config.enable_logging is True
        assert config.log_level == "INFO"
        assert config.log_requests is True
        assert config.log_responses is True
        assert config.log_errors is True
        assert "authorization" in config.sensitive_headers
        assert "x-api-key" in config.sensitive_headers
    
    def test_logging_config_custom_values(self):
        """Test LoggingConfig with custom values."""
        config = LoggingConfig(
            enable_logging=False,
            log_level="DEBUG",
            log_requests=False,
            log_responses=False,
            log_errors=False,
            sensitive_headers=["custom-header"]
        )
        
        assert config.enable_logging is False
        assert config.log_level == "DEBUG"
        assert config.log_requests is False
        assert config.log_responses is False
        assert config.log_errors is False
        assert config.sensitive_headers == ["custom-header"]


class TestHTTPClientSettings:
    """Test HTTPClientSettings class."""
    
    def test_http_client_settings_defaults(self):
        """Test HTTPClientSettings default values."""
        settings = HTTPClientSettings()
        
        assert settings.base_url is None
        assert isinstance(settings.timeout, TimeoutConfig)
        assert isinstance(settings.retry, RetryConfig)
        assert isinstance(settings.auth, AuthConfig)
        assert isinstance(settings.connection_pool, ConnectionPoolConfig)
        assert isinstance(settings.rate_limit, RateLimitConfig)
        assert isinstance(settings.circuit_breaker, CircuitBreakerConfig)
        assert isinstance(settings.logging, LoggingConfig)
        assert settings.headers == {}
        assert settings.verify_ssl is True
        assert settings.follow_redirects is True
    
    def test_http_client_settings_custom_values(self):
        """Test HTTPClientSettings with custom values."""
        settings = HTTPClientSettings(
            base_url="https://api.example.com",
            headers={"X-Custom": "value"},
            verify_ssl=False,
            follow_redirects=False
        )
        
        assert settings.base_url == "https://api.example.com"
        assert settings.headers == {"X-Custom": "value"}
        assert settings.verify_ssl is False
        assert settings.follow_redirects is False
    
    def test_http_client_settings_to_dict(self):
        """Test HTTPClientSettings to_dict method."""
        settings = HTTPClientSettings(
            base_url="https://api.example.com",
            headers={"X-Custom": "value"}
        )
        
        result = settings.to_dict()
        
        assert result["base_url"] == "https://api.example.com"
        assert result["headers"] == {"X-Custom": "value"}
        assert result["verify_ssl"] is True
        assert result["follow_redirects"] is True
        assert "timeout" in result
        assert "retry" in result
        assert "auth" in result
        assert "connection_pool" in result
        assert "rate_limit" in result
        assert "circuit_breaker" in result
        assert "logging" in result


class TestCircuitBreakerState:
    """Test CircuitBreakerState enum."""
    
    def test_circuit_breaker_state_values(self):
        """Test CircuitBreakerState enum values."""
        assert CircuitBreakerState.CLOSED.value == "closed"
        assert CircuitBreakerState.OPEN.value == "open"
        assert CircuitBreakerState.HALF_OPEN.value == "half_open"
    
    def test_circuit_breaker_state_names(self):
        """Test CircuitBreakerState enum names."""
        assert CircuitBreakerState.CLOSED.name == "CLOSED"
        assert CircuitBreakerState.OPEN.name == "OPEN"
        assert CircuitBreakerState.HALF_OPEN.name == "HALF_OPEN"
