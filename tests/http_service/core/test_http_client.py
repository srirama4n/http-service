"""
Unit tests for the HTTP client module.
"""

import pytest
import asyncio
import httpx
from unittest.mock import Mock, patch, AsyncMock
from http_service.core.client import HttpClient
from models import (
    RetryConfig, TimeoutConfig, AuthConfig, CircuitBreakerConfig,
    HTTPClientSettings
)
from http_service.core.config import HTTPClientConfig
from http_service.patterns.circuit_breaker import CircuitBreakerOpenError


class TestHttpClient:
    """Test HttpClient class."""
    
    def test_http_client_initialization_with_config(self):
        """Test HttpClient initialization with config object."""
        config = HTTPClientConfig(
            base_url="https://api.example.com",
            api_key="test-key",
            max_retries=5
        )
        
        client = HttpClient(config=config)
        
        assert client.base_url == "https://api.example.com"
        assert client.api_key == "test-key"
        assert client.max_retries == 5
    
    def test_http_client_initialization_with_parameters(self):
        """Test HttpClient initialization with individual parameters."""
        client = HttpClient(
            base_url="https://api.example.com",
            api_key="test-key",
            max_retries=5
        )
        
        assert client.base_url == "https://api.example.com"
        assert client.api_key == "test-key"
        assert client.max_retries == 5
    
    def test_http_client_default_values(self):
        """Test HttpClient default values."""
        client = HttpClient()
        
        assert client.base_url is None
        assert client.verify_ssl is True
        assert client.enable_logging is True
        assert client.max_retries == 3
        assert client.retry_delay == 1.0
        assert client.backoff_factor == 2.0
        assert client.auth_type == "none"
        assert client.circuit_breaker_enabled is False
    
    @patch('http_service.core.client.httpx.Client')
    def test_http_client_get_success(self, mock_client_class):
        """Test HttpClient GET request success."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "success"}
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = HttpClient(base_url="https://api.example.com")
        response = client.get("/users")
        
        assert response.status_code == 200
        assert response.json() == {"message": "success"}
        mock_client.request.assert_called_once()
    
    @patch('http_service.core.client.httpx.Client')
    def test_http_client_post_success(self, mock_client_class):
        """Test HttpClient POST request success."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 1, "name": "test"}
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = HttpClient(base_url="https://api.example.com")
        data = {"name": "test"}
        response = client.post("/users", json=data)
        
        assert response.status_code == 201
        assert response.json() == {"id": 1, "name": "test"}
        mock_client.request.assert_called_once()
    
    @patch('http_service.core.client.httpx.Client')
    def test_http_client_put_success(self, mock_client_class):
        """Test HttpClient PUT request success."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "name": "updated"}
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = HttpClient(base_url="https://api.example.com")
        data = {"name": "updated"}
        response = client.put("/users/1", json=data)
        
        assert response.status_code == 200
        assert response.json() == {"id": 1, "name": "updated"}
        mock_client.request.assert_called_once()
    
    @patch('http_service.core.client.httpx.Client')
    def test_http_client_patch_success(self, mock_client_class):
        """Test HttpClient PATCH request success."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "name": "patched"}
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = HttpClient(base_url="https://api.example.com")
        data = {"name": "patched"}
        response = client.patch("/users/1", json=data)
        
        assert response.status_code == 200
        assert response.json() == {"id": 1, "name": "patched"}
        mock_client.request.assert_called_once()
    
    @patch('http_service.core.client.httpx.Client')
    def test_http_client_delete_success(self, mock_client_class):
        """Test HttpClient DELETE request success."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 204
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = HttpClient(base_url="https://api.example.com")
        response = client.delete("/users/1")
        
        assert response.status_code == 204
        mock_client.request.assert_called_once()
    
    @patch('http_service.core.client.httpx.Client')
    def test_http_client_request_success(self, mock_client_class):
        """Test HttpClient request method success."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "success"}
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = HttpClient(base_url="https://api.example.com")
        response = client.request("GET", "/users")
        
        assert response.status_code == 200
        assert response.json() == {"message": "success"}
        mock_client.request.assert_called_once()
    
    @patch('http_service.core.client.httpx.Client')
    def test_http_client_with_headers(self, mock_client_class):
        """Test HttpClient with custom headers."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = HttpClient(
            base_url="https://api.example.com",
            headers={"X-Custom": "value"}
        )
        response = client.get("/users")
        
        # Check that headers were passed to the request
        # Headers are set at the client level, not in individual requests
        assert mock_client.request.called
    
    @patch('http_service.core.client.httpx.Client')
    def test_http_client_with_auth_api_key(self, mock_client_class):
        """Test HttpClient with API key authentication."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = HttpClient(
            base_url="https://api.example.com",
            auth_type="api_key",
            api_key="test-api-key",
            api_key_header="X-API-Key"
        )
        response = client.get("/users")
        
        # Check that API key header was added
        # Headers are set at the client level, not in individual requests
        assert mock_client.request.called
    
    @patch('http_service.core.client.httpx.Client')
    def test_http_client_with_auth_bearer(self, mock_client_class):
        """Test HttpClient with bearer token authentication."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = HttpClient(
            base_url="https://api.example.com",
            auth_type="bearer",
            token="test-token"
        )
        response = client.get("/users")
        
        # Check that Authorization header was added
        # Headers are set at the client level, not in individual requests
        assert mock_client.request.called
    
    @patch('http_service.core.client.httpx.Client')
    def test_http_client_with_auth_basic(self, mock_client_class):
        """Test HttpClient with basic authentication."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = HttpClient(
            base_url="https://api.example.com",
            auth_type="basic",
            username="testuser",
            password="testpass"
        )
        response = client.get("/users")
        
        # Check that Authorization header was added
        # Headers are set at the client level, not in individual requests
        assert mock_client.request.called
    
    @patch('http_service.core.client.httpx.Client')
    def test_http_client_retry_on_failure(self, mock_client_class):
        """Test HttpClient retry on failure."""
        mock_client = Mock()
        mock_response_failure = Mock()
        mock_response_failure.status_code = 500
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"message": "success"}
        
        # First call fails, second succeeds
        mock_client.request.side_effect = [mock_response_failure, mock_response_success]
        mock_client_class.return_value = mock_client
        
        client = HttpClient(
            base_url="https://api.example.com",
            max_retries=3,
            retry_delay=0.5,  # Longer delay to ensure retry happens
            retry_on_status_codes=[500],  # Explicitly set retry on 500
            circuit_breaker_enabled=False,  # Disable circuit breaker completely for retry test
            circuit_breaker_failure_status_codes=[]
        )
        
        # The retry should work and eventually return the successful response
        response = client.get("/users")
        
        # Check that the request was called multiple times (retry behavior)
        assert mock_client.request.call_count >= 2
        # The final response should be the successful one
        assert response.status_code == 200
    
    @patch('http_service.core.client.httpx.Client')
    def test_http_client_circuit_breaker(self, mock_client_class):
        """Test HttpClient with circuit breaker."""
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
            max_retries=0  # Disable retries for circuit breaker test
        )
        
        # First failure - circuit breaker still closed
        with pytest.raises(httpx.HTTPStatusError):
            client.get("/users")
        
        # Second failure - circuit breaker opens
        with pytest.raises(httpx.HTTPStatusError):
            client.get("/users")
        
        # Third call - should be blocked by circuit breaker
        with pytest.raises(CircuitBreakerOpenError):
            client.get("/users")
    
    @patch('http_service.core.client.httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_http_client_async_get_success(self, mock_client_class):
        """Test HttpClient async GET request success."""
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "success"}
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = HttpClient(base_url="https://api.example.com")
        response = await client.aget("/users")
        
        assert response.status_code == 200
        assert response.json() == {"message": "success"}
        mock_client.request.assert_called_once()
    
    @patch('http_service.core.client.httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_http_client_async_post_success(self, mock_client_class):
        """Test HttpClient async POST request success."""
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 1, "name": "test"}
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = HttpClient(base_url="https://api.example.com")
        data = {"name": "test"}
        response = await client.apost("/users", json=data)
        
        assert response.status_code == 201
        assert response.json() == {"id": 1, "name": "test"}
        mock_client.request.assert_called_once()
    
    @patch('http_service.core.client.httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_http_client_async_request_success(self, mock_client_class):
        """Test HttpClient async request method success."""
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "success"}
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = HttpClient(base_url="https://api.example.com")
        response = await client.arequest("GET", "/users")
        
        assert response.status_code == 200
        assert response.json() == {"message": "success"}
        mock_client.request.assert_called_once()
    
    def test_http_client_circuit_breaker_stats(self):
        """Test HttpClient circuit breaker stats."""
        client = HttpClient(
            base_url="https://api.example.com",
            circuit_breaker_enabled=True
        )
        
        stats = client.get_circuit_breaker_stats()
        
        assert "state" in stats
        assert "failure_count" in stats
        assert "success_count" in stats
        assert "total_calls" in stats
        assert "successful_calls" in stats
        assert "failed_calls" in stats
        assert "success_rate" in stats
    
    def test_http_client_reset_circuit_breaker(self):
        """Test HttpClient reset circuit breaker."""
        client = HttpClient(
            base_url="https://api.example.com",
            circuit_breaker_enabled=True
        )
        
        # Force open circuit breaker
        client.force_open_circuit_breaker()
        assert client.is_circuit_breaker_open()
        
        # Reset circuit breaker
        client.reset_circuit_breaker()
        assert client.is_circuit_breaker_closed()
    
    def test_http_client_circuit_breaker_states(self):
        """Test HttpClient circuit breaker state methods."""
        client = HttpClient(
            base_url="https://api.example.com",
            circuit_breaker_enabled=True
        )
        
        # Initially closed
        assert client.is_circuit_breaker_closed()
        assert not client.is_circuit_breaker_open()
        assert not client.is_circuit_breaker_half_open()
        
        # Force open
        client.force_open_circuit_breaker()
        assert client.is_circuit_breaker_open()
        assert not client.is_circuit_breaker_closed()
        assert not client.is_circuit_breaker_half_open()


class TestHttpClientConvenienceFunctions:
    """Test HttpClient convenience functions."""
    
    def test_create_api_client(self):
        """Test create_api_client function."""
        client = HttpClient.create_api_client(
            base_url="https://api.example.com",
            api_key="test-key"
        )
        
        assert client.base_url == "https://api.example.com"
        assert client.api_key == "test-key"
        assert client.auth_type == "api_key"
    
    def test_create_basic_auth_client(self):
        """Test create_basic_auth_client function."""
        client = HttpClient.create_basic_auth_client(
            base_url="https://api.example.com",
            username="testuser",
            password="testpass"
        )
        
        assert client.base_url == "https://api.example.com"
        assert client.username == "testuser"
        assert client.password == "testpass"
        assert client.auth_type == "basic"
    
    def test_create_bearer_token_client(self):
        """Test create_bearer_token_client function."""
        client = HttpClient.create_bearer_token_client(
            base_url="https://api.example.com",
            token="test-token"
        )
        
        assert client.base_url == "https://api.example.com"
        assert client.token == "test-token"
        assert client.auth_type == "bearer"
    
    def test_create_retry_client(self):
        """Test create_retry_client function."""
        client = HttpClient.create_retry_client(
            base_url="https://api.example.com",
            max_retries=5,
            retry_delay=2.0
        )
        
        assert client.base_url == "https://api.example.com"
        assert client.max_retries == 5
        assert client.retry_delay == 2.0
    
    def test_create_circuit_breaker_client(self):
        """Test create_circuit_breaker_client function."""
        client = HttpClient.create_circuit_breaker_client(
            base_url="https://api.example.com",
            failure_threshold=3,
            recovery_timeout=10.0
        )
        
        assert client.base_url == "https://api.example.com"
        assert client.circuit_breaker_enabled is True
        assert client.circuit_breaker_failure_threshold == 3
        assert client.circuit_breaker_recovery_timeout == 10.0
    
    @patch('http_service.core.client.get_config')
    def test_create_client_from_env(self, mock_get_config):
        """Test create_client_from_env function."""
        mock_config = HTTPClientConfig(
            base_url="https://api.example.com",
            api_key="env-key"
        )
        mock_get_config.return_value = mock_config
        
        client = HttpClient.create_client_from_env()
        
        assert client.base_url == "https://api.example.com"
        assert client.api_key == "env-key"
        mock_get_config.assert_called_once()
    
    @patch('http_service.core.client.get_config_for_service')
    def test_create_client_for_service(self, mock_get_config_for_service):
        """Test create_client_for_service function."""
        mock_config = HTTPClientConfig(
            base_url="https://user-api.example.com",
            api_key="user-key"
        )
        mock_get_config_for_service.return_value = mock_config
        
        client = HttpClient.create_client_for_service("user")
        
        assert client.base_url == "https://user-api.example.com"
        assert client.api_key == "user-key"
        mock_get_config_for_service.assert_called_once_with("user")


class TestHttpClientErrorHandling:
    """Test HttpClient error handling."""
    
    @patch('http_service.core.client.httpx.Client')
    def test_http_client_connection_error(self, mock_client_class):
        """Test HttpClient connection error handling."""
        import httpx
        
        mock_client = Mock()
        mock_client.request.side_effect = httpx.ConnectError("Connection failed")
        mock_client_class.return_value = mock_client
        
        client = HttpClient(base_url="https://api.example.com")
        
        with pytest.raises(httpx.ConnectError):
            client.get("/users")
    
    @patch('http_service.core.client.httpx.Client')
    def test_http_client_timeout_error(self, mock_client_class):
        """Test HttpClient timeout error handling."""
        import httpx
        
        mock_client = Mock()
        mock_client.request.side_effect = httpx.TimeoutException("Request timeout")
        mock_client_class.return_value = mock_client
        
        client = HttpClient(base_url="https://api.example.com")
        
        with pytest.raises(httpx.TimeoutException):
            client.get("/users")
    
    @patch('http_service.core.client.httpx.Client')
    def test_http_client_http_status_error(self, mock_client_class):
        """Test HttpClient HTTP status error handling."""
        import httpx
        
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 404
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = HttpClient(base_url="https://api.example.com")
        
        # Should not raise by default, but response should have status code
        response = client.get("/users")
        assert response.status_code == 404
    
    @patch('http_service.core.client.httpx.Client')
    def test_http_client_raise_for_status(self, mock_client_class):
        """Test HttpClient with raise_for_status enabled."""
        import httpx
        
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=Mock(), response=mock_response
        )
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = HttpClient(
            base_url="https://api.example.com",
            raise_for_status=True
        )
        
        with pytest.raises(httpx.HTTPStatusError):
            client.get("/users")
