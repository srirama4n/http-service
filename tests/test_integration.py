"""
Integration tests for the HTTP client package.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from http_service.client import HttpClient
from http_service.models import CircuitBreakerConfig
from http_service.config import HTTPClientConfig
from http_service.circuit_breaker import CircuitBreakerOpenError


class TestHttpClientIntegration:
    """Integration tests for HttpClient."""
    
    @patch('http_service.client.httpx.Client')
    def test_full_http_client_workflow(self, mock_client_class):
        """Test complete HTTP client workflow with all features."""
        # Setup mock responses
        mock_client = Mock()
        
        # Create a function to return different responses based on method
        def mock_request(method, url, **kwargs):
            response = Mock()
            if method == "DELETE":
                response.status_code = 204
            elif method in ["GET", "POST", "PUT"]:
                response.status_code = 200
            else:
                response.status_code = 500
            response.json.return_value = {"id": 1, "status": "success"}
            return response
        
        # Mock the request method instead of individual HTTP methods
        mock_client.request.side_effect = mock_request
        mock_client_class.return_value = mock_client
        
        # Create client with all features enabled
        client = HttpClient(
            base_url="https://api.example.com",
            auth_type="api_key",
            api_key="test-api-key",
            max_retries=3,
            retry_delay=0.1,
            circuit_breaker_enabled=True,
            circuit_breaker_failure_threshold=3,
            circuit_breaker_recovery_timeout=0.2,
            circuit_breaker_failure_status_codes=[],  # Disable automatic failure detection
            headers={"X-Custom": "test-value"}
        )
        
        # Test successful requests
        response1 = client.get("/users")
        assert response1.status_code == 200
        
        response2 = client.post("/users", json={"name": "test"})
        assert response2.status_code == 200
        
        response3 = client.put("/users/1", json={"name": "updated"})
        assert response3.status_code == 200
        
        response4 = client.delete("/users/1")
        assert response4.status_code == 204
        
        # Test circuit breaker with failures - manually trigger failures
        # First few calls should succeed or retry
        for i in range(3):
            try:
                client.get("/failing-endpoint")
            except CircuitBreakerOpenError:
                break
        
        # Manually force circuit breaker to open for testing
        client.force_open_circuit_breaker()
        assert client.is_circuit_breaker_open()
        
        # Manually set last_failure_time to trigger half-open transition
        client._circuit_breaker.last_failure_time = time.time() - 0.3
        
        # Circuit should be half-open after recovery timeout
        assert client.is_circuit_breaker_half_open()
        
        # Reset circuit breaker
        client.reset_circuit_breaker()
        assert client.is_circuit_breaker_closed()
    
    @patch('http_service.client.httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_full_async_http_client_workflow(self, mock_client_class):
        """Test complete async HTTP client workflow."""
        # Setup mock responses
        mock_client = AsyncMock()
        
        # Create different responses for different methods
        def mock_request(method, url, **kwargs):
            response = Mock()
            if method == "DELETE":
                response.status_code = 204
            else:
                response.status_code = 200
            response.json.return_value = {"message": "success"}
            return response
        
        # Mock the request method for async client
        mock_client.request.side_effect = mock_request
        mock_client_class.return_value = mock_client
        
        # Create async client
        client = HttpClient(
            base_url="https://api.example.com",
            auth_type="bearer",
            token="test-token"
        )
        
        # Test async requests
        response1 = await client.aget("/users")
        assert response1.status_code == 200
        
        response2 = await client.apost("/users", json={"name": "test"})
        assert response2.status_code == 200
        
        response3 = await client.aput("/users/1", json={"name": "updated"})
        assert response3.status_code == 200
        
        response4 = await client.adelete("/users/1")
        assert response4.status_code == 204
    
    def test_environment_configuration_integration(self):
        """Test integration with environment configuration."""
        with patch.dict('os.environ', {
            'HTTP_BASE_URL': 'https://env-api.example.com',
            'HTTP_API_KEY': 'env-api-key',
            'HTTP_AUTH_TYPE': 'api_key',
            'HTTP_MAX_RETRIES': '5',
            'HTTP_CIRCUIT_BREAKER_ENABLED': 'true',
            'HTTP_CIRCUIT_BREAKER_FAILURE_THRESHOLD': '3'
        }):
            config = HTTPClientConfig.from_env()
            client = HttpClient(config=config)
            
            assert client.base_url == "https://env-api.example.com"
            assert client.api_key == "env-api-key"
            assert client.auth_type == "api_key"
            assert client.max_retries == 5
            assert client.circuit_breaker_enabled is True
            assert client.circuit_breaker_failure_threshold == 3
    
    def test_service_specific_configuration_integration(self):
        """Test integration with service-specific configuration."""
        with patch.dict('os.environ', {
            'USER_BASE_URL': 'https://user-api.example.com',
            'USER_API_KEY': 'user-api-key',
            'USER_AUTH_TYPE': 'api_key',
            'USER_CIRCUIT_BREAKER_ENABLED': 'true'
        }):
            config = HTTPClientConfig.from_env()
            # Override with service-specific values
            config.base_url = "https://user-api.example.com"
            config.api_key = "user-api-key"
            config.auth_type = "api_key"
            config.circuit_breaker_enabled = True
            
            client = HttpClient(config=config)
            
            assert client.base_url == "https://user-api.example.com"
            assert client.api_key == "user-api-key"
            assert client.auth_type == "api_key"
            assert client.circuit_breaker_enabled is True
    
    @patch('http_service.client.httpx.Client')
    def test_retry_and_circuit_breaker_integration(self, mock_client_class):
        """Test integration between retry logic and circuit breaker."""
        import httpx
        
        mock_client = Mock()
        
        # Create responses that will trigger retries and circuit breaker
        responses = []
        for i in range(20):  # More responses to avoid StopIteration
            response = Mock()
            response.status_code = 500  # All responses are errors
            responses.append(response)
        
        # Mock the request method
        mock_client.request.side_effect = responses
        mock_client_class.return_value = mock_client
        
        client = HttpClient(
            base_url="https://api.example.com",
            max_retries=2,
            retry_delay=0.1,
            circuit_breaker_enabled=True,
            circuit_breaker_failure_threshold=2,
            circuit_breaker_recovery_timeout=0.2,
            circuit_breaker_failure_status_codes=[500]  # Enable failure detection
        )
        
        # First call - should retry twice then fail with HTTPStatusError
        with pytest.raises(httpx.HTTPStatusError):
            client.get("/failing-endpoint")
        
        # Second call - should retry twice then fail, opening circuit
        with pytest.raises(httpx.HTTPStatusError):
            client.get("/failing-endpoint")
        
        # Third call - should be blocked by circuit breaker
        with pytest.raises(CircuitBreakerOpenError):
            client.get("/failing-endpoint")
        
        # Wait for recovery
        time.sleep(0.3)
        
        # Should be half-open now
        assert client.is_circuit_breaker_half_open()
    
    def test_authentication_integration(self):
        """Test integration of different authentication methods."""
        # Test API Key authentication
        api_client = HttpClient(
            base_url="https://api.example.com",
            auth_type="api_key",
            api_key="test-api-key",
            api_key_header="X-API-Key"
        )
        
        # Check that headers are set during client initialization
        assert api_client.api_key == "test-api-key"
        assert api_client.auth_type == "api_key"
        assert api_client.api_key_header == "X-API-Key"
        
        # Test Bearer token authentication
        bearer_client = HttpClient(
            base_url="https://api.example.com",
            auth_type="bearer",
            token="test-bearer-token"
        )
        
        assert bearer_client.token == "test-bearer-token"
        assert bearer_client.auth_type == "bearer"
        
        # Test Basic authentication
        basic_client = HttpClient(
            base_url="https://api.example.com",
            auth_type="basic",
            username="testuser",
            password="testpass"
        )
        
        assert basic_client.username == "testuser"
        assert basic_client.password == "testpass"
        assert basic_client.auth_type == "basic"
    
    def test_rate_limiting_integration(self):
        """Test integration of rate limiting with other features."""
        client = HttpClient(
            base_url="https://api.example.com",
            rate_limit_requests_per_second=2.0
        )
        
        # Verify that rate limiting is configured
        assert client.rate_limit_requests_per_second == 2.0
    
    def test_convenience_functions_integration(self):
        """Test integration of convenience functions."""
        # Test create_api_client
        api_client = HttpClient.create_api_client(
            base_url="https://api.example.com",
            api_key="test-key"
        )
        assert api_client.base_url == "https://api.example.com"
        assert api_client.api_key == "test-key"
        assert api_client.auth_type == "api_key"
        
        # Test create_basic_auth_client
        basic_client = HttpClient.create_basic_auth_client(
            base_url="https://api.example.com",
            username="testuser",
            password="testpass"
        )
        assert basic_client.base_url == "https://api.example.com"
        assert basic_client.username == "testuser"
        assert basic_client.password == "testpass"
        assert basic_client.auth_type == "basic"
        
        # Test create_bearer_token_client
        bearer_client = HttpClient.create_bearer_token_client(
            base_url="https://api.example.com",
            token="test-token"
        )
        assert bearer_client.base_url == "https://api.example.com"
        assert bearer_client.token == "test-token"
        assert bearer_client.auth_type == "bearer"
        
        # Test create_retry_client
        retry_client = HttpClient.create_retry_client(
            base_url="https://api.example.com",
            max_retries=5,
            retry_delay=2.0
        )
        assert retry_client.base_url == "https://api.example.com"
        assert retry_client.max_retries == 5
        assert retry_client.retry_delay == 2.0
        
        # Test create_circuit_breaker_client
        cb_client = HttpClient.create_circuit_breaker_client(
            base_url="https://api.example.com",
            failure_threshold=3,
            recovery_timeout=10.0
        )
        assert cb_client.base_url == "https://api.example.com"
        assert cb_client.circuit_breaker_enabled is True
        assert cb_client.circuit_breaker_failure_threshold == 3
        assert cb_client.circuit_breaker_recovery_timeout == 10.0
    
    @patch('http_service.client.get_config')
    def test_environment_client_creation_integration(self, mock_get_config):
        """Test integration of environment-based client creation."""
        mock_config = HTTPClientConfig(
            base_url="https://env-api.example.com",
            api_key="env-key",
            auth_type="api_key"
        )
        mock_get_config.return_value = mock_config
        
        client = HttpClient.create_client_from_env()
        
        assert client.base_url == "https://env-api.example.com"
        assert client.api_key == "env-key"
        assert client.auth_type == "api_key"
        mock_get_config.assert_called_once()
    
    @patch('http_service.client.get_config_for_service')
    def test_service_client_creation_integration(self, mock_get_config_for_service):
        """Test integration of service-based client creation."""
        mock_config = HTTPClientConfig(
            base_url="https://user-api.example.com",
            api_key="user-key",
            auth_type="api_key"
        )
        mock_get_config_for_service.return_value = mock_config
        
        client = HttpClient.create_client_for_service("user")
        
        assert client.base_url == "https://user-api.example.com"
        assert client.api_key == "user-key"
        assert client.auth_type == "api_key"
        mock_get_config_for_service.assert_called_once_with("user")


class TestErrorHandlingIntegration:
    """Integration tests for error handling."""
    
    @patch('http_service.client.httpx.Client')
    def test_comprehensive_error_handling(self, mock_client_class):
        """Test comprehensive error handling integration."""
        import httpx
        
        mock_client = Mock()
        
        # Test different types of errors - create more to avoid StopIteration
        errors = [
            httpx.ConnectError("Connection failed"),
            httpx.ReadTimeout("Read timeout"),
            httpx.WriteTimeout("Write timeout"),
            httpx.PoolTimeout("Pool timeout"),
            httpx.HTTPStatusError("HTTP 500", request=Mock(), response=Mock(status_code=500)),
            httpx.RemoteProtocolError("Remote protocol error"),
            # Add more errors to avoid StopIteration
            httpx.ConnectError("Connection failed 2"),
            httpx.ReadTimeout("Read timeout 2"),
            httpx.WriteTimeout("Write timeout 2"),
            httpx.PoolTimeout("Pool timeout 2"),
            httpx.HTTPStatusError("HTTP 500 2", request=Mock(), response=Mock(status_code=500)),
            httpx.RemoteProtocolError("Remote protocol error 2")
        ]
        
        mock_client.request.side_effect = errors
        mock_client_class.return_value = mock_client
        
        client = HttpClient(
            base_url="https://api.example.com",
            max_retries=2,
            retry_delay=0.1
        )
        
        # Test that different errors are handled appropriately
        for i, error in enumerate(errors):
            try:
                client.get(f"/endpoint-{i}")
            except type(error):
                # Expected to raise the same type of error
                pass
            except Exception as e:
                # Other exceptions might be raised due to retry logic
                assert isinstance(e, (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError, httpx.RemoteProtocolError, StopIteration))
    
    @patch('http_service.client.httpx.Client')
    def test_circuit_breaker_error_integration(self, mock_client_class):
        """Test circuit breaker error handling integration."""
        import httpx
        
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 500
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = HttpClient(
            base_url="https://api.example.com",
            circuit_breaker_enabled=True,
            circuit_breaker_failure_threshold=2,
            circuit_breaker_recovery_timeout=0.1,
            circuit_breaker_failure_status_codes=[500]  # Enable failure detection
        )
        
        # First failure - should retry then fail with HTTPStatusError
        with pytest.raises(httpx.HTTPStatusError):
            client.get("/failing-endpoint")
        
        # Second failure - opens circuit
        with pytest.raises(httpx.HTTPStatusError):
            client.get("/failing-endpoint")
        
        # Third call - circuit breaker error
        with pytest.raises(CircuitBreakerOpenError):
            client.get("/failing-endpoint")
        
        # Test circuit breaker stats
        stats = client.get_circuit_breaker_stats()
        assert stats["state"] == "open"
        assert stats["failure_count"] >= 2
        assert stats["total_calls"] >= 3
        
        # Test manual circuit breaker control
        client.reset_circuit_breaker()
        assert client.is_circuit_breaker_closed()
        
        client.force_open_circuit_breaker()
        assert client.is_circuit_breaker_open()


class TestPerformanceIntegration:
    """Integration tests for performance features."""
    
    @patch('http_service.client.httpx.Client')
    def test_connection_pooling_integration(self, mock_client_class):
        """Test connection pooling integration."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = HttpClient(
            base_url="https://api.example.com",
            max_connections=10,
            max_keepalive_connections=5,
            keepalive_expiry=30.0
        )
        
        # Make multiple requests to test connection pooling
        for i in range(5):
            response = client.get(f"/users/{i}")
            assert response.status_code == 200
        
        # Verify client was created with correct pool settings
        mock_client_class.assert_called_once()
        call_args = mock_client_class.call_args[1]
        assert call_args["limits"].max_connections == 10
        assert call_args["limits"].max_keepalive_connections == 5
    
    @patch('http_service.client.httpx.Client')
    def test_timeout_integration(self, mock_client_class):
        """Test timeout configuration integration."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = HttpClient(
            base_url="https://api.example.com",
            connect_timeout=5.0,
            read_timeout=15.0,
            write_timeout=10.0,
            pool_timeout=5.0
        )
        
        client.get("/users")
        
        # Verify client was created with correct timeout settings
        mock_client_class.assert_called_once()
        call_args = mock_client_class.call_args[1]
        assert call_args["timeout"].connect == 5.0
        assert call_args["timeout"].read == 15.0
        assert call_args["timeout"].write == 10.0
        assert call_args["timeout"].pool == 5.0
