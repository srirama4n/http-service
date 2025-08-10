"""
HTTP Client module.

This module provides the main HttpClient class that integrates all the
modular components (retry, circuit breaker, authentication, etc.).
"""

import asyncio
import logging
import time
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import httpx

from .config import HTTPClientConfig, get_config, get_config_for_service
from .models import (
    RetryConfig, TimeoutConfig, AuthConfig, CircuitBreakerConfig,
    HTTPClientSettings
)
from .circuit_breaker import CircuitBreaker, CircuitBreakerOpenError, should_trigger_circuit_breaker
from .utils import (
    build_url, sanitize_headers, format_request_log, format_response_log,
    merge_headers, create_auth_header
)
from .decorators import retry, async_retry, rate_limit, async_rate_limit

logger = logging.getLogger(__name__)


class HttpClient:
    """
    A comprehensive HTTP client with retry logic, circuit breaker, and authentication.
    
    This client provides a high-level interface for making HTTP requests with
    built-in support for retry logic, circuit breaker pattern, rate limiting,
    authentication, and comprehensive logging.
    """
    
    def __init__(
        self,
        config: Optional[HTTPClientConfig] = None,
        base_url: Optional[str] = None,
        verify_ssl: bool = True,
        enable_logging: bool = True,
        connect_timeout: float = 10.0,
        read_timeout: float = 30.0,
        write_timeout: float = 30.0,
        pool_timeout: float = 10.0,
        max_connections: int = 10,
        max_keepalive_connections: int = 5,
        keepalive_expiry: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        backoff_factor: float = 2.0,
        retry_on_status_codes: Optional[list] = None,
        rate_limit_requests_per_second: Optional[float] = None,
        circuit_breaker_enabled: bool = False,
        circuit_breaker_failure_threshold: int = 5,
        circuit_breaker_recovery_timeout: float = 60.0,
        circuit_breaker_failure_status_codes: Optional[list] = None,
        circuit_breaker_success_threshold: int = 2,
        auth_type: str = "none",
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        api_key: Optional[str] = None,
        api_key_header: str = "X-API-Key",
        headers: Optional[Dict[str, str]] = None,
        follow_redirects: bool = True,
        raise_for_status: bool = False,
        # Certificate settings
        ca_cert_file: Optional[str] = None,
        ca_cert_data: Optional[str] = None,
        client_cert_file: Optional[str] = None,
        client_key_file: Optional[str] = None,
        client_cert_data: Optional[str] = None,
        client_key_data: Optional[str] = None,
        check_hostname: bool = True,
        cert_reqs: str = "CERT_REQUIRED",
        ssl_version: Optional[str] = None,
        ciphers: Optional[str] = None,
        cert_verify_mode: Optional[str] = None
    ):
        """
        Initialize the HTTP client.
        
        Args:
            config: Configuration object (if provided, other parameters are ignored)
            base_url: Base URL for all requests
            verify_ssl: Whether to verify SSL certificates
            enable_logging: Whether to enable request/response logging
            connect_timeout: Connection timeout in seconds
            read_timeout: Read timeout in seconds
            write_timeout: Write timeout in seconds
            pool_timeout: Pool timeout in seconds
            max_connections: Maximum number of connections in the pool
            max_keepalive_connections: Maximum number of keepalive connections
            keepalive_expiry: Keepalive expiry time in seconds
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
            backoff_factor: Exponential backoff factor
            retry_on_status_codes: HTTP status codes to retry on
            rate_limit_requests_per_second: Rate limit in requests per second
            circuit_breaker_enabled: Whether to enable circuit breaker
            circuit_breaker_failure_threshold: Number of failures before opening circuit
            circuit_breaker_recovery_timeout: Time to wait before half-opening circuit
            circuit_breaker_failure_status_codes: Status codes that trigger circuit breaker
            circuit_breaker_success_threshold: Number of successes to close circuit
            auth_type: Authentication type ('none', 'basic', 'bearer', 'api_key')
            username: Username for basic authentication
            password: Password for basic authentication
            token: Bearer token
            api_key: API key
            api_key_header: Header name for API key
            headers: Additional headers
            follow_redirects: Whether to follow redirects
            raise_for_status: Whether to raise exceptions for HTTP errors
        """
        if config:
            # Use configuration object
            self._init_from_config(config)
        else:
            # Use individual parameters
            self._init_from_params(
                base_url=base_url,
                verify_ssl=verify_ssl,
                enable_logging=enable_logging,
                connect_timeout=connect_timeout,
                read_timeout=read_timeout,
                write_timeout=write_timeout,
                pool_timeout=pool_timeout,
                max_connections=max_connections,
                max_keepalive_connections=max_keepalive_connections,
                keepalive_expiry=keepalive_expiry,
                max_retries=max_retries,
                retry_delay=retry_delay,
                backoff_factor=backoff_factor,
                retry_on_status_codes=retry_on_status_codes,
                rate_limit_requests_per_second=rate_limit_requests_per_second,
                circuit_breaker_enabled=circuit_breaker_enabled,
                circuit_breaker_failure_threshold=circuit_breaker_failure_threshold,
                circuit_breaker_recovery_timeout=circuit_breaker_recovery_timeout,
                circuit_breaker_failure_status_codes=circuit_breaker_failure_status_codes,
                circuit_breaker_success_threshold=circuit_breaker_success_threshold,
                auth_type=auth_type,
                username=username,
                password=password,
                token=token,
                api_key=api_key,
                api_key_header=api_key_header,
                headers=headers,
                follow_redirects=follow_redirects,
                raise_for_status=raise_for_status
            )
        
        # Initialize circuit breaker after parameters are set
        failure_status_codes = self.circuit_breaker_failure_status_codes if self.circuit_breaker_failure_status_codes is not None else [500, 502, 503, 504]
        self._circuit_breaker = CircuitBreaker(
            CircuitBreakerConfig(
                enabled=self.circuit_breaker_enabled,
                failure_threshold=self.circuit_breaker_failure_threshold,
                recovery_timeout=self.circuit_breaker_recovery_timeout,
                failure_status_codes=failure_status_codes,
                success_threshold=self.circuit_breaker_success_threshold
            )
        )
        
        # Initialize HTTPX client
        self._init_httpx_client()
    
    def _init_from_config(self, config: HTTPClientConfig):
        """Initialize from configuration object."""
        self.base_url = config.base_url
        self.verify_ssl = config.verify_ssl
        self.enable_logging = config.enable_logging
        self.connect_timeout = config.connect_timeout
        self.read_timeout = config.read_timeout
        self.write_timeout = config.write_timeout
        self.pool_timeout = config.pool_timeout
        self.max_connections = config.max_connections
        self.max_keepalive_connections = config.max_keepalive_connections
        self.keepalive_expiry = config.keepalive_expiry
        self.max_retries = config.max_retries
        self.retry_delay = config.retry_delay
        self.backoff_factor = config.backoff_factor
        self.retry_on_status_codes = config.retry_on_status_codes
        self.rate_limit_requests_per_second = config.rate_limit_requests_per_second
        self.circuit_breaker_enabled = config.circuit_breaker_enabled
        self.circuit_breaker_failure_threshold = config.circuit_breaker_failure_threshold
        self.circuit_breaker_recovery_timeout = config.circuit_breaker_recovery_timeout
        self.circuit_breaker_failure_status_codes = config.circuit_breaker_failure_status_codes
        self.circuit_breaker_success_threshold = config.circuit_breaker_success_threshold
        self.auth_type = config.auth_type
        self.username = config.username
        self.password = config.password
        self.token = config.token
        self.api_key = config.api_key
        self.api_key_header = config.api_key_header
        self.headers = config.custom_headers or {}
        self.follow_redirects = True
        self.raise_for_status = False
        
        # Certificate settings
        self.ca_cert_file = config.ca_cert_file
        self.ca_cert_data = config.ca_cert_data
        self.client_cert_file = config.client_cert_file
        self.client_key_file = config.client_key_file
        self.client_cert_data = config.client_cert_data
        self.client_key_data = config.client_key_data
        self.check_hostname = config.check_hostname
        self.cert_reqs = config.cert_reqs
        self.ssl_version = config.ssl_version
        self.ciphers = config.ciphers
        self.cert_verify_mode = config.cert_verify_mode
    
    def _init_from_params(self, **kwargs):
        """Initialize from individual parameters."""
        self.base_url = kwargs.get('base_url')
        self.verify_ssl = kwargs.get('verify_ssl', True)
        self.enable_logging = kwargs.get('enable_logging', True)
        self.connect_timeout = kwargs.get('connect_timeout', 10.0)
        self.read_timeout = kwargs.get('read_timeout', 30.0)
        self.write_timeout = kwargs.get('write_timeout', 30.0)
        self.pool_timeout = kwargs.get('pool_timeout', 10.0)
        self.max_connections = kwargs.get('max_connections', 10)
        self.max_keepalive_connections = kwargs.get('max_keepalive_connections', 5)
        self.keepalive_expiry = kwargs.get('keepalive_expiry', 30.0)
        self.max_retries = kwargs.get('max_retries', 3)
        self.retry_delay = kwargs.get('retry_delay', 1.0)
        self.backoff_factor = kwargs.get('backoff_factor', 2.0)
        self.retry_on_status_codes = kwargs.get('retry_on_status_codes', [429, 500, 502, 503, 504])
        self.rate_limit_requests_per_second = kwargs.get('rate_limit_requests_per_second')
        self.circuit_breaker_enabled = kwargs.get('circuit_breaker_enabled', False)
        self.circuit_breaker_failure_threshold = kwargs.get('circuit_breaker_failure_threshold', 5)
        self.circuit_breaker_recovery_timeout = kwargs.get('circuit_breaker_recovery_timeout', 60.0)
        self.circuit_breaker_failure_status_codes = kwargs.get('circuit_breaker_failure_status_codes', [500, 502, 503, 504])
        self.circuit_breaker_success_threshold = kwargs.get('circuit_breaker_success_threshold', 2)
        self.auth_type = kwargs.get('auth_type', 'none')
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.token = kwargs.get('token')
        self.api_key = kwargs.get('api_key')
        self.api_key_header = kwargs.get('api_key_header', 'X-API-Key')
        self.headers = kwargs.get('headers', {})
        self.follow_redirects = kwargs.get('follow_redirects', True)
        self.raise_for_status = kwargs.get('raise_for_status', False)
        
        # Certificate settings
        self.ca_cert_file = kwargs.get('ca_cert_file')
        self.ca_cert_data = kwargs.get('ca_cert_data')
        self.client_cert_file = kwargs.get('client_cert_file')
        self.client_key_file = kwargs.get('client_key_file')
        self.client_cert_data = kwargs.get('client_cert_data')
        self.client_key_data = kwargs.get('client_key_data')
        self.check_hostname = kwargs.get('check_hostname', True)
        self.cert_reqs = kwargs.get('cert_reqs', "CERT_REQUIRED")
        self.ssl_version = kwargs.get('ssl_version')
        self.ciphers = kwargs.get('ciphers')
        self.cert_verify_mode = kwargs.get('cert_verify_mode')
    
    def _init_httpx_client(self):
        """Initialize the HTTPX client with configuration."""
        # Create timeout configuration
        timeout = httpx.Timeout(
            connect=self.connect_timeout,
            read=self.read_timeout,
            write=self.write_timeout,
            pool=self.pool_timeout
        )
        
        # Create limits configuration
        limits = httpx.Limits(
            max_connections=self.max_connections,
            max_keepalive_connections=self.max_keepalive_connections,
            keepalive_expiry=self.keepalive_expiry
        )
        
        # Create authentication
        auth = None
        if self.auth_type == "basic" and self.username and self.password:
            auth = httpx.BasicAuth(self.username, self.password)
        
        # Create headers
        headers = self.headers.copy() if self.headers else {}
        
        # Add authentication headers
        if self.auth_type == "bearer" and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        elif self.auth_type == "api_key" and self.api_key:
            headers[self.api_key_header] = self.api_key
        
        # Build SSL context for certificates
        ssl_context = self._build_ssl_context()
        
        # Determine verify setting based on verify_ssl flag and SSL context
        verify_setting = self._determine_verify_setting(ssl_context)
        
        # Create the client
        client_kwargs = {
            'timeout': timeout,
            'limits': limits,
            'auth': auth,
            'headers': headers,
            'verify': verify_setting,
            'follow_redirects': self.follow_redirects
        }
        
        # Only add base_url if it's provided
        if self.base_url:
            client_kwargs['base_url'] = self.base_url
        
        self._client = httpx.Client(**client_kwargs)
        self._async_client = httpx.AsyncClient(**client_kwargs)
    
    def _retry_decorator(self, func):
        """Create retry decorator for the client."""
        if self.max_retries == 0:
            return func
        return retry(
            max_retries=self.max_retries,
            retry_delay=self.retry_delay,
            backoff_factor=self.backoff_factor,
            retry_on_status_codes=self.retry_on_status_codes
        )(func)
    
    def _async_retry_decorator(self, func):
        """Create async retry decorator for the client."""
        return async_retry(
            max_retries=self.max_retries,
            retry_delay=self.retry_delay,
            backoff_factor=self.backoff_factor,
            retry_on_status_codes=self.retry_on_status_codes
        )(func)
    
    def _rate_limit_decorator(self, func):
        """Create rate limit decorator for the client."""
        if self.rate_limit_requests_per_second:
            return rate_limit(requests_per_second=self.rate_limit_requests_per_second)(func)
        return func
    
    def _async_rate_limit_decorator(self, func):
        """Create async rate limit decorator for the client."""
        if self.rate_limit_requests_per_second:
            return async_rate_limit(requests_per_second=self.rate_limit_requests_per_second)(func)
        return func
    
    def _make_request(self, method: str, url: str, **kwargs):
        """Make an HTTP request with circuit breaker and retry logic."""
        def request_func():
            response = self._client.request(method, url, **kwargs)
            
            # Check if response status code should trigger circuit breaker
            if (self.circuit_breaker_enabled and 
                self._circuit_breaker.config.failure_status_codes and 
                len(self._circuit_breaker.config.failure_status_codes) > 0 and
                response.status_code in self._circuit_breaker.config.failure_status_codes):
                # Raise an exception to trigger circuit breaker
                import httpx
                raise httpx.HTTPStatusError(
                    f"{response.status_code} {response.reason_phrase}",
                    request=response.request,
                    response=response
                )
            
            return response
        
        # Apply decorators
        decorated_func = self._retry_decorator(self._rate_limit_decorator(request_func))
        
        # Wrap with circuit breaker if enabled
        if self.circuit_breaker_enabled:
            final_func = lambda: self._circuit_breaker.call(decorated_func)
        else:
            final_func = decorated_func
        
        try:
            response = final_func()
            
            # Raise for status if configured
            if self.raise_for_status:
                response.raise_for_status()
            
            return response
            
        except CircuitBreakerOpenError:
            # Re-raise circuit breaker errors
            raise
        except Exception as e:
            # Let the circuit breaker handle failures automatically
            raise
    
    def _determine_verify_setting(self, ssl_context):
        """Determine the verify setting based on verify_ssl flag and SSL context."""
        # If verify_ssl is False, disable verification regardless of SSL context
        if not self.verify_ssl:
            return False
        
        # If verify_ssl is True but no SSL context, use default verification
        if not ssl_context:
            return True
        
        # If verify_ssl is True and SSL context exists, use the SSL context
        return ssl_context
    
    def _build_ssl_context(self):
        """Build SSL context for certificate configuration."""
        import ssl
        
        # If verify_ssl is False, return None to disable verification
        if not self.verify_ssl:
            return None
        
        # If no certificate configuration, return None to use default
        if not any([
            self.ca_cert_file, self.ca_cert_data,
            self.client_cert_file, self.client_key_file,
            self.client_cert_data, self.client_key_data,
            self.ssl_version, self.ciphers
        ]):
            return None
        
        # Create SSL context
        ssl_context = ssl.create_default_context()
        
        # Configure CA certificates
        if self.ca_cert_file:
            ssl_context.load_verify_locations(cafile=self.ca_cert_file)
        elif self.ca_cert_data:
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write(self.ca_cert_data)
                temp_ca_file = f.name
            ssl_context.load_verify_locations(cafile=temp_ca_file)
        
        # Configure client certificates
        if self.client_cert_file and self.client_key_file:
            ssl_context.load_cert_chain(
                certfile=self.client_cert_file,
                keyfile=self.client_key_file
            )
        elif self.client_cert_data and self.client_key_data:
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as cert_file:
                cert_file.write(self.client_cert_data)
                temp_cert_file = cert_file.name
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as key_file:
                key_file.write(self.client_key_data)
                temp_key_file = key_file.name
            
            ssl_context.load_cert_chain(
                certfile=temp_cert_file,
                keyfile=temp_key_file
            )
        
        # Configure certificate verification
        if self.cert_reqs == "CERT_NONE":
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        elif self.cert_reqs == "CERT_OPTIONAL":
            ssl_context.check_hostname = self.check_hostname
            ssl_context.verify_mode = ssl.CERT_OPTIONAL
        else:  # CERT_REQUIRED (default)
            ssl_context.check_hostname = self.check_hostname
            ssl_context.verify_mode = ssl.CERT_REQUIRED
        
        # Configure SSL version
        if self.ssl_version:
            if self.ssl_version == "TLSv1_2":
                ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
                ssl_context.maximum_version = ssl.TLSVersion.TLSv1_2
            elif self.ssl_version == "TLSv1_3":
                ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3
                ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3
        
        # Configure ciphers
        if self.ciphers:
            ssl_context.set_ciphers(self.ciphers)
        
        return ssl_context
        
        try:
            response = decorated_func()
            
            # Check if response should trigger circuit breaker
            if self.circuit_breaker_enabled and should_trigger_circuit_breaker(
                response, None, self._circuit_breaker.config
            ):
                self._circuit_breaker.record_failure()
            
            # Raise for status if configured
            if self.raise_for_status:
                response.raise_for_status()
            
            return response
            
        except CircuitBreakerOpenError:
            # Re-raise circuit breaker errors
            raise
        except Exception as e:
            # Record failure in circuit breaker
            if self.circuit_breaker_enabled:
                self._circuit_breaker.record_failure()
            raise
    
    async def _make_async_request(self, method: str, url: str, **kwargs):
        """Make an async HTTP request with circuit breaker and retry logic."""
        async def request_func():
            # Check circuit breaker
            if self.circuit_breaker_enabled:
                return await self._circuit_breaker.acall(
                    lambda: self._async_client.request(method, url, **kwargs)
                )
            else:
                return await self._async_client.request(method, url, **kwargs)
        
        # Apply decorators
        decorated_func = self._async_retry_decorator(self._async_rate_limit_decorator(request_func))
        
        try:
            response = await decorated_func()
            
            # Check if response status code should trigger circuit breaker
            if (self.circuit_breaker_enabled and 
                self._circuit_breaker.config.failure_status_codes and 
                response.status_code in self._circuit_breaker.config.failure_status_codes):
                # Raise an exception to trigger circuit breaker
                import httpx
                raise httpx.HTTPStatusError(
                    f"{response.status_code} {response.reason_phrase}",
                    request=response.request,
                    response=response
                )
            
            # Raise for status if configured
            if self.raise_for_status:
                response.raise_for_status()
            
            return response
            
        except CircuitBreakerOpenError:
            # Re-raise circuit breaker errors
            raise
        except Exception as e:
            # Let the circuit breaker handle failures automatically
            raise
    
    def get(self, url: str, **kwargs):
        """Make a GET request."""
        return self._make_request("GET", url, **kwargs)
    
    def post(self, url: str, **kwargs):
        """Make a POST request."""
        return self._make_request("POST", url, **kwargs)
    
    def put(self, url: str, **kwargs):
        """Make a PUT request."""
        return self._make_request("PUT", url, **kwargs)
    
    def patch(self, url: str, **kwargs):
        """Make a PATCH request."""
        return self._make_request("PATCH", url, **kwargs)
    
    def delete(self, url: str, **kwargs):
        """Make a DELETE request."""
        return self._make_request("DELETE", url, **kwargs)
    
    def request(self, method: str, url: str, **kwargs):
        """Make a request with the specified method."""
        return self._make_request(method, url, **kwargs)
    
    async def aget(self, url: str, **kwargs):
        """Make an async GET request."""
        return await self._make_async_request("GET", url, **kwargs)
    
    async def apost(self, url: str, **kwargs):
        """Make an async POST request."""
        return await self._make_async_request("POST", url, **kwargs)
    
    async def aput(self, url: str, **kwargs):
        """Make an async PUT request."""
        return await self._make_async_request("PUT", url, **kwargs)
    
    async def apatch(self, url: str, **kwargs):
        """Make an async PATCH request."""
        return await self._make_async_request("PATCH", url, **kwargs)
    
    async def adelete(self, url: str, **kwargs):
        """Make an async DELETE request."""
        return await self._make_async_request("DELETE", url, **kwargs)
    
    async def arequest(self, method: str, url: str, **kwargs):
        """Make an async request with the specified method."""
        return await self._make_async_request(method, url, **kwargs)
    
    # Circuit breaker management methods
    def get_circuit_breaker_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        return self._circuit_breaker.get_stats()
    
    def reset_circuit_breaker(self):
        """Reset the circuit breaker to closed state."""
        self._circuit_breaker.reset()
    
    def force_open_circuit_breaker(self):
        """Force the circuit breaker to open state."""
        self._circuit_breaker.force_open()
    
    def is_circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is open."""
        return self._circuit_breaker.is_open()
    
    def is_circuit_breaker_closed(self) -> bool:
        """Check if circuit breaker is closed."""
        return self._circuit_breaker.is_closed()
    
    def is_circuit_breaker_half_open(self) -> bool:
        """Check if circuit breaker is half-open."""
        return self._circuit_breaker.is_half_open()
    
    def close(self):
        """Close the HTTP client and free resources."""
        self._client.close()
    
    async def aclose(self):
        """Close the async HTTP client and free resources."""
        await self._async_client.aclose()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.aclose()
    
    # Convenience factory methods
    @classmethod
    def create_api_client(cls, base_url: str, api_key: str, **kwargs):
        """Create a client configured for API key authentication."""
        return cls(base_url=base_url, auth_type="api_key", api_key=api_key, **kwargs)
    
    @classmethod
    def create_basic_auth_client(cls, base_url: str, username: str, password: str, **kwargs):
        """Create a client configured for basic authentication."""
        return cls(base_url=base_url, auth_type="basic", username=username, password=password, **kwargs)
    
    @classmethod
    def create_bearer_token_client(cls, base_url: str, token: str, **kwargs):
        """Create a client configured for bearer token authentication."""
        return cls(base_url=base_url, auth_type="bearer", token=token, **kwargs)
    
    @classmethod
    def create_retry_client(cls, base_url: str, max_retries: int = 5, retry_delay: float = 1.0, **kwargs):
        """Create a client with enhanced retry configuration."""
        return cls(base_url=base_url, max_retries=max_retries, retry_delay=retry_delay, **kwargs)
    
    @classmethod
    def create_circuit_breaker_client(cls, base_url: str, failure_threshold: int = 3, recovery_timeout: float = 10.0, **kwargs):
        """Create a client with circuit breaker enabled."""
        return cls(
            base_url=base_url,
            circuit_breaker_enabled=True,
            circuit_breaker_failure_threshold=failure_threshold,
            circuit_breaker_recovery_timeout=recovery_timeout,
            **kwargs
        )
    
    @classmethod
    def create_client_from_env(cls):
        """Create a client from environment configuration."""
        config = get_config()
        return cls(config=config)
    
    @classmethod
    def create_client_for_service(cls, service_name: str):
        """Create a client for a specific service from environment configuration."""
        config = get_config_for_service(service_name)
        return cls(config=config)
