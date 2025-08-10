"""
Unit tests for the config module.
"""

import os
import pytest
from unittest.mock import patch, mock_open
from http_service.config import HTTPClientConfig, get_config, get_config_for_service


class TestHTTPClientConfig:
    """Test HTTPClientConfig class."""
    
    def test_http_client_config_defaults(self):
        """Test HTTPClientConfig default values."""
        config = HTTPClientConfig()
        
        assert config.base_url is None
        assert config.verify_ssl is True
        assert config.enable_logging is True
        assert config.connect_timeout == 10.0
        assert config.read_timeout == 30.0
        assert config.write_timeout == 30.0
        assert config.pool_timeout == 10.0
        assert config.max_connections == 10
        assert config.max_keepalive_connections == 5
        assert config.keepalive_expiry == 30.0
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
        assert config.backoff_factor == 2.0
        assert config.retry_on_status_codes == [429, 500, 502, 503, 504]
        assert config.rate_limit_requests_per_second is None
        assert config.circuit_breaker_enabled is False
        assert config.circuit_breaker_failure_threshold == 5
        assert config.circuit_breaker_recovery_timeout == 60.0
        assert config.circuit_breaker_failure_status_codes == [500, 502, 503, 504]
        assert config.circuit_breaker_success_threshold == 2
        assert config.auth_type == "none"
        assert config.username is None
        assert config.password is None
        assert config.token is None
        assert config.api_key is None
        assert config.api_key_header == "X-API-Key"
        assert config.custom_headers == {}
    
    def test_http_client_config_custom_values(self):
        """Test HTTPClientConfig with custom values."""
        config = HTTPClientConfig(
            base_url="https://api.example.com",
            verify_ssl=False,
            enable_logging=False,
            connect_timeout=5.0,
            read_timeout=15.0,
            write_timeout=20.0,
            pool_timeout=5.0,
            max_connections=20,
            max_keepalive_connections=10,
            keepalive_expiry=60.0,
            max_retries=5,
            retry_delay=2.0,
            backoff_factor=1.5,
            retry_on_status_codes=[500, 502],
            rate_limit_requests_per_second=10.0,
            circuit_breaker_enabled=True,
            circuit_breaker_failure_threshold=3,
            circuit_breaker_recovery_timeout=30.0,
            circuit_breaker_failure_status_codes=[500, 502],
            circuit_breaker_success_threshold=1,
            auth_type="api_key",
            username="testuser",
            password="testpass",
            token="test-token",
            api_key="test-api-key",
            api_key_header="X-Custom-Key",
            custom_headers={"X-Test": "value"}
        )
        
        assert config.base_url == "https://api.example.com"
        assert config.verify_ssl is False
        assert config.enable_logging is False
        assert config.connect_timeout == 5.0
        assert config.read_timeout == 15.0
        assert config.write_timeout == 20.0
        assert config.pool_timeout == 5.0
        assert config.max_connections == 20
        assert config.max_keepalive_connections == 10
        assert config.keepalive_expiry == 60.0
        assert config.max_retries == 5
        assert config.retry_delay == 2.0
        assert config.backoff_factor == 1.5
        assert config.retry_on_status_codes == [500, 502]
        assert config.rate_limit_requests_per_second == 10.0
        assert config.circuit_breaker_enabled is True
        assert config.circuit_breaker_failure_threshold == 3
        assert config.circuit_breaker_recovery_timeout == 30.0
        assert config.circuit_breaker_failure_status_codes == [500, 502]
        assert config.circuit_breaker_success_threshold == 1
        assert config.auth_type == "api_key"
        assert config.username == "testuser"
        assert config.password == "testpass"
        assert config.token == "test-token"
        assert config.api_key == "test-api-key"
        assert config.api_key_header == "X-Custom-Key"
        assert config.custom_headers == {"X-Test": "value"}
    
    def test_http_client_config_to_dict(self):
        """Test HTTPClientConfig to_dict method."""
        config = HTTPClientConfig(
            base_url="https://api.example.com",
            api_key="test-key",
            custom_headers={"X-Test": "value"}
        )
        
        result = config.to_dict()
        
        assert result["base_url"] == "https://api.example.com"
        assert result["api_key"] == "test-key"
        assert result["custom_headers"] == {"X-Test": "value"}
        assert "connect_timeout" in result
        assert "read_timeout" in result
        assert "write_timeout" in result
        assert "pool_timeout" in result
        assert "max_connections" in result
        assert "max_keepalive_connections" in result
        assert "keepalive_expiry" in result
        assert "max_retries" in result
        assert "retry_delay" in result
        assert "backoff_factor" in result
        assert "retry_on_status_codes" in result
        assert "rate_limit_requests_per_second" in result
        assert "circuit_breaker_enabled" in result
        assert "circuit_breaker_failure_threshold" in result
        assert "circuit_breaker_recovery_timeout" in result
        assert "circuit_breaker_failure_status_codes" in result
        assert "circuit_breaker_success_threshold" in result
        assert "auth_type" in result
        assert "username" in result
        assert "password" in result
        assert "token" in result
        assert "api_key_header" in result


class TestHTTPClientConfigFromEnv:
    """Test HTTPClientConfig.from_env method."""
    
    @patch.dict(os.environ, {
        'HTTP_BASE_URL': 'https://api.example.com',
        'HTTP_VERIFY_SSL': 'false',
        'HTTP_ENABLE_LOGGING': 'false',
        'HTTP_CONNECT_TIMEOUT': '5.0',
        'HTTP_READ_TIMEOUT': '15.0',
        'HTTP_WRITE_TIMEOUT': '20.0',
        'HTTP_POOL_TIMEOUT': '5.0',
        'HTTP_MAX_CONNECTIONS': '20',
        'HTTP_MAX_KEEPALIVE_CONNECTIONS': '10',
        'HTTP_KEEPALIVE_EXPIRY': '60.0',
        'HTTP_MAX_RETRIES': '5',
        'HTTP_RETRY_DELAY': '2.0',
        'HTTP_BACKOFF_FACTOR': '1.5',
        'HTTP_RETRY_STATUS_CODES': '500,502',
        'HTTP_RATE_LIMIT_RPS': '10.0',
        'HTTP_CIRCUIT_BREAKER_ENABLED': 'true',
        'HTTP_CIRCUIT_BREAKER_FAILURE_THRESHOLD': '3',
        'HTTP_CIRCUIT_BREAKER_RECOVERY_TIMEOUT': '30.0',
        'HTTP_CIRCUIT_BREAKER_FAILURE_STATUS_CODES': '500,502',
        'HTTP_CIRCUIT_BREAKER_SUCCESS_THRESHOLD': '1',
        'HTTP_AUTH_TYPE': 'api_key',
        'HTTP_USERNAME': 'testuser',
        'HTTP_PASSWORD': 'testpass',
        'HTTP_TOKEN': 'test-token',
        'HTTP_API_KEY': 'test-api-key',
        'HTTP_API_KEY_HEADER': 'X-Custom-Key',
        'HTTP_HEADER_X_TEST': 'test-value',
        'HTTP_HEADER_X_CUSTOM': 'custom-value'
    })
    def test_from_env_with_all_values(self):
        """Test from_env with all environment variables set."""
        config = HTTPClientConfig.from_env()
        
        assert config.base_url == "https://api.example.com"
        assert config.verify_ssl is False
        assert config.enable_logging is False
        assert config.connect_timeout == 5.0
        assert config.read_timeout == 15.0
        assert config.write_timeout == 20.0
        assert config.pool_timeout == 5.0
        assert config.max_connections == 20
        assert config.max_keepalive_connections == 10
        assert config.keepalive_expiry == 60.0
        assert config.max_retries == 5
        assert config.retry_delay == 2.0
        assert config.backoff_factor == 1.5
        assert config.retry_on_status_codes == [500, 502]
        assert config.rate_limit_requests_per_second == 10.0
        assert config.circuit_breaker_enabled is True
        assert config.circuit_breaker_failure_threshold == 3
        assert config.circuit_breaker_recovery_timeout == 30.0
        assert config.circuit_breaker_failure_status_codes == [500, 502]
        assert config.circuit_breaker_success_threshold == 1
        assert config.auth_type == "api_key"
        assert config.username == "testuser"
        assert config.password == "testpass"
        assert config.token == "test-token"
        assert config.api_key == "test-api-key"
        assert config.api_key_header == "X-Custom-Key"
        assert config.custom_headers == {
            "x-test": "test-value",
            "x-custom": "custom-value"
        }
    
    @patch.dict(os.environ, {}, clear=True)
    def test_from_env_with_no_values(self):
        """Test from_env with no environment variables set."""
        config = HTTPClientConfig.from_env()
        
        assert config.base_url is None
        assert config.verify_ssl is True
        assert config.enable_logging is True
        assert config.connect_timeout == 10.0
        assert config.read_timeout == 30.0
        assert config.write_timeout == 30.0
        assert config.pool_timeout == 10.0
        assert config.max_connections == 10
        assert config.max_keepalive_connections == 5
        assert config.keepalive_expiry == 30.0
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
        assert config.backoff_factor == 2.0
        assert config.retry_on_status_codes == [429, 500, 502, 503, 504]
        assert config.rate_limit_requests_per_second is None
        assert config.circuit_breaker_enabled is False
        assert config.circuit_breaker_failure_threshold == 5
        assert config.circuit_breaker_recovery_timeout == 60.0
        assert config.circuit_breaker_failure_status_codes == [500, 502, 503, 504]
        assert config.circuit_breaker_success_threshold == 2
        assert config.auth_type == "none"
        assert config.username is None
        assert config.password is None
        assert config.token is None
        assert config.api_key is None
        assert config.api_key_header == "X-API-Key"
        assert config.custom_headers == {}
    
    @patch.dict(os.environ, {
        'HTTP_VERIFY_SSL': 'invalid',
        'HTTP_ENABLE_LOGGING': 'invalid',
        'HTTP_CIRCUIT_BREAKER_ENABLED': 'invalid'
    })
    def test_from_env_with_invalid_boolean_values(self):
        """Test from_env with invalid boolean values."""
        config = HTTPClientConfig.from_env()
        
        # Should default to True for invalid values
        assert config.verify_ssl is True
        assert config.enable_logging is True
        assert config.circuit_breaker_enabled is False
    
    def test_parse_custom_headers(self):
        """Test _parse_custom_headers method."""
        with patch.dict(os.environ, {
            'HTTP_HEADER_X_TEST': 'test-value',
            'HTTP_HEADER_X_CUSTOM': 'custom-value',
            'HTTP_HEADER_AUTHORIZATION': 'Bearer token',
            'OTHER_VAR': 'other-value'
        }):
            headers = HTTPClientConfig._parse_custom_headers()
            
            assert headers == {
                "x-test": "test-value",
                "x-custom": "custom-value",
                "authorization": "Bearer token"
            }


class TestGetConfig:
    """Test get_config function."""
    
    @patch('http_service.config.HTTPClientConfig.from_env')
    def test_get_config(self, mock_from_env):
        """Test get_config function."""
        mock_config = HTTPClientConfig(base_url="https://api.example.com")
        mock_from_env.return_value = mock_config
        
        result = get_config()
        
        assert result == mock_config
        mock_from_env.assert_called_once()


class TestGetConfigForService:
    """Test get_config_for_service function."""
    
    @patch.dict(os.environ, {
        'USER_BASE_URL': 'https://user-api.example.com',
        'USER_API_KEY': 'user-api-key',
        'USER_AUTH_TYPE': 'api_key',
        'USER_VERIFY_SSL': 'true',
        'USER_ENABLE_LOGGING': 'false',
        'USER_CONNECT_TIMEOUT': '5.0',
        'USER_READ_TIMEOUT': '15.0',
        'USER_MAX_RETRIES': '5',
        'USER_RETRY_DELAY': '2.0',
        'USER_BACKOFF_FACTOR': '1.5',
        'USER_RETRY_STATUS_CODES': '500,502',
        'USER_RATE_LIMIT_RPS': '10.0',
        'USER_CIRCUIT_BREAKER_ENABLED': 'true',
        'USER_CIRCUIT_BREAKER_FAILURE_THRESHOLD': '3',
        'USER_CIRCUIT_BREAKER_RECOVERY_TIMEOUT': '30.0',
        'USER_CIRCUIT_BREAKER_FAILURE_STATUS_CODES': '500,502',
        'USER_CIRCUIT_BREAKER_SUCCESS_THRESHOLD': '1',
        'USER_HEADER_X_CUSTOM': 'user-custom-value'
    })
    @patch('http_service.config.HTTPClientConfig.from_env')
    def test_get_config_for_service_with_user_prefix(self, mock_from_env):
        """Test get_config_for_service with USER_ prefix."""
        base_config = HTTPClientConfig()
        mock_from_env.return_value = base_config
        
        result = get_config_for_service("user")
        
        assert result.base_url == "https://user-api.example.com"
        assert result.api_key == "user-api-key"
        assert result.auth_type == "api_key"
        assert result.verify_ssl is True
        assert result.enable_logging is False
        assert result.connect_timeout == 5.0
        assert result.read_timeout == 15.0
        assert result.max_retries == 5
        assert result.retry_delay == 2.0
        assert result.backoff_factor == 1.5
        assert result.retry_on_status_codes == [500, 502]
        assert result.rate_limit_requests_per_second == 10.0
        assert result.circuit_breaker_enabled is True
        assert result.circuit_breaker_failure_threshold == 3
        assert result.circuit_breaker_recovery_timeout == 30.0
        assert result.circuit_breaker_failure_status_codes == [500, 502]
        assert result.circuit_breaker_success_threshold == 1
        assert result.custom_headers == {"x-custom": "user-custom-value"}
    
    @patch.dict(os.environ, {
        'ORDER_BASE_URL': 'https://order-api.example.com',
        'ORDER_TOKEN': 'order-token',
        'ORDER_AUTH_TYPE': 'bearer'
    })
    @patch('http_service.config.HTTPClientConfig.from_env')
    def test_get_config_for_service_with_order_prefix(self, mock_from_env):
        """Test get_config_for_service with ORDER_ prefix."""
        base_config = HTTPClientConfig()
        mock_from_env.return_value = base_config
        
        result = get_config_for_service("order")
        
        assert result.base_url == "https://order-api.example.com"
        assert result.token == "order-token"
        assert result.auth_type == "bearer"
    
    @patch.dict(os.environ, {
        'PAYMENT_BASE_URL': 'https://payment-api.example.com',
        'PAYMENT_USERNAME': 'payment-user',
        'PAYMENT_PASSWORD': 'payment-pass'
    })
    @patch('http_service.config.HTTPClientConfig.from_env')
    def test_get_config_for_service_with_payment_prefix(self, mock_from_env):
        """Test get_config_for_service with PAYMENT_ prefix."""
        base_config = HTTPClientConfig()
        mock_from_env.return_value = base_config
        
        result = get_config_for_service("payment")
        
        assert result.base_url == "https://payment-api.example.com"
        assert result.username == "payment-user"
        assert result.password == "payment-pass"
        assert result.auth_type == "basic"
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('http_service.config.HTTPClientConfig.from_env')
    def test_get_config_for_service_with_no_service_vars(self, mock_from_env):
        """Test get_config_for_service with no service-specific variables."""
        base_config = HTTPClientConfig(
            base_url="https://default.example.com",
            max_retries=5,
            connect_timeout=15.0,
            circuit_breaker_enabled=True
        )
        mock_from_env.return_value = base_config
        
        result = get_config_for_service("nonexistent")
        
        # Should return base config with default values preserved
        assert result.base_url == "https://default.example.com"
        assert result.auth_type == "none"
        assert result.max_retries == 5
        assert result.connect_timeout == 15.0
        assert result.circuit_breaker_enabled is True
        assert result.verify_ssl is True  # Default value
        assert result.enable_logging is True  # Default value
        assert result.read_timeout == 30.0  # Default value
        assert result.max_connections == 10  # Default value
    
    @patch.dict(os.environ, {
        'PARTIAL_BASE_URL': 'https://partial-api.example.com',
        'PARTIAL_MAX_RETRIES': '7',
        'PARTIAL_CIRCUIT_BREAKER_ENABLED': 'true'
    })
    @patch('http_service.config.HTTPClientConfig.from_env')
    def test_get_config_for_service_with_partial_config(self, mock_from_env):
        """Test get_config_for_service with only some service-specific variables set."""
        base_config = HTTPClientConfig(
            base_url="https://default.example.com",
            max_retries=3,
            connect_timeout=10.0,
            circuit_breaker_enabled=False
        )
        mock_from_env.return_value = base_config
        
        result = get_config_for_service("partial")
        
        # Should use service-specific values where provided
        assert result.base_url == "https://partial-api.example.com"
        assert result.max_retries == 7
        assert result.circuit_breaker_enabled is True
        
        # Should use base config defaults for unspecified values
        assert result.connect_timeout == 10.0
        assert result.auth_type == "none"
        assert result.verify_ssl is True
        assert result.enable_logging is True
        assert result.read_timeout == 30.0
        assert result.max_connections == 10
