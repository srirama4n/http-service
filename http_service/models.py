"""
Data models for HTTP client configuration.
Contains dataclasses for retry, timeout, and authentication settings.
"""

import httpx
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service is recovered


@dataclass
class RetryConfig:
    """Configuration for retry logic."""
    max_retries: int = 3
    retry_delay: float = 1.0
    backoff_factor: float = 2.0
    retry_on_status_codes: List[int] = field(default_factory=lambda: [429, 500, 502, 503, 504])
    retry_on_exceptions: List[type] = field(default_factory=lambda: [
        httpx.ConnectTimeout,
        httpx.ReadTimeout,
        httpx.WriteTimeout,
        httpx.PoolTimeout,
        httpx.RemoteProtocolError,
        httpx.ConnectError,
        httpx.ReadError,
        httpx.WriteError
    ])


@dataclass
class TimeoutConfig:
    """Configuration for timeout settings."""
    connect_timeout: float = 10.0
    read_timeout: float = 30.0
    write_timeout: float = 30.0
    pool_timeout: float = 10.0


@dataclass
class AuthConfig:
    """Configuration for authentication."""
    auth_type: str = "none"  # "none", "basic", "bearer", "api_key"
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    api_key: Optional[str] = None
    api_key_header: str = "X-API-Key"


@dataclass
class ConnectionPoolConfig:
    """Configuration for connection pooling."""
    max_connections: int = 10
    max_keepalive_connections: int = 5
    keepalive_expiry: float = 30.0


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    requests_per_second: Optional[float] = None
    burst_size: Optional[int] = None


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker pattern."""
    enabled: bool = False
    failure_threshold: int = 5  # Number of failures to open circuit
    recovery_timeout: float = 60.0  # Time to wait before trying half-open
    expected_exception: type = Exception  # Exception type to count as failure
    failure_status_codes: List[int] = field(default_factory=lambda: [500, 502, 503, 504])
    success_threshold: int = 2  # Number of successes to close circuit
    timeout_exceptions: List[type] = field(default_factory=lambda: [
        httpx.ConnectTimeout,
        httpx.ReadTimeout,
        httpx.WriteTimeout,
        httpx.PoolTimeout
    ])


@dataclass
class LoggingConfig:
    """Configuration for logging."""
    enable_logging: bool = True
    log_level: str = "INFO"
    log_requests: bool = True
    log_responses: bool = True
    log_errors: bool = True
    sensitive_headers: List[str] = field(default_factory=lambda: [
        "authorization", "x-api-key", "cookie", "set-cookie"
    ])


@dataclass
class CertificateConfig:
    """Configuration for SSL/TLS certificates."""
    # Server certificate verification
    verify_ssl: bool = True
    ca_cert_file: Optional[str] = None  # Path to CA certificate file
    ca_cert_data: Optional[str] = None  # CA certificate data as string
    
    # Client certificates for mutual TLS
    client_cert_file: Optional[str] = None  # Path to client certificate file
    client_key_file: Optional[str] = None   # Path to client private key file
    client_cert_data: Optional[str] = None  # Client certificate data as string
    client_key_data: Optional[str] = None   # Client private key data as string
    
    # Certificate validation options
    check_hostname: bool = True  # Verify hostname in certificate
    cert_reqs: str = "CERT_REQUIRED"  # Certificate requirements: CERT_NONE, CERT_OPTIONAL, CERT_REQUIRED
    
    # Additional SSL options
    ssl_version: Optional[str] = None  # SSL/TLS version (e.g., "TLSv1_2", "TLSv1_3")
    ciphers: Optional[str] = None      # SSL ciphers to use
    cert_verify_mode: Optional[str] = None  # Certificate verification mode


@dataclass
class HTTPClientSettings:
    """Complete HTTP client settings."""
    base_url: Optional[str] = None
    timeout: TimeoutConfig = field(default_factory=TimeoutConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    connection_pool: ConnectionPoolConfig = field(default_factory=ConnectionPoolConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    circuit_breaker: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    certificate: CertificateConfig = field(default_factory=CertificateConfig)
    headers: Dict[str, str] = field(default_factory=dict)
    verify_ssl: bool = True
    follow_redirects: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            'base_url': self.base_url,
            'timeout': {
                'connect_timeout': self.timeout.connect_timeout,
                'read_timeout': self.timeout.read_timeout,
                'write_timeout': self.timeout.write_timeout,
                'pool_timeout': self.timeout.pool_timeout
            },
            'retry': {
                'max_retries': self.retry.max_retries,
                'retry_delay': self.retry.retry_delay,
                'backoff_factor': self.retry.backoff_factor,
                'retry_on_status_codes': self.retry.retry_on_status_codes
            },
            'auth': {
                'auth_type': self.auth.auth_type,
                'username': self.auth.username,
                'token': self.auth.token,
                'api_key': self.auth.api_key,
                'api_key_header': self.auth.api_key_header
            },
            'connection_pool': {
                'max_connections': self.connection_pool.max_connections,
                'max_keepalive_connections': self.connection_pool.max_keepalive_connections,
                'keepalive_expiry': self.connection_pool.keepalive_expiry
            },
            'rate_limit': {
                'requests_per_second': self.rate_limit.requests_per_second,
                'burst_size': self.rate_limit.burst_size
            },
            'circuit_breaker': {
                'enabled': self.circuit_breaker.enabled,
                'failure_threshold': self.circuit_breaker.failure_threshold,
                'recovery_timeout': self.circuit_breaker.recovery_timeout,
                'failure_status_codes': self.circuit_breaker.failure_status_codes,
                'success_threshold': self.circuit_breaker.success_threshold
            },
            'logging': {
                'enable_logging': self.logging.enable_logging,
                'log_level': self.logging.log_level,
                'log_requests': self.logging.log_requests,
                'log_responses': self.logging.log_responses,
                'log_errors': self.logging.log_errors
            },
            'certificate': {
                'verify_ssl': self.certificate.verify_ssl,
                'ca_cert_file': self.certificate.ca_cert_file,
                'ca_cert_data': self.certificate.ca_cert_data,
                'client_cert_file': self.certificate.client_cert_file,
                'client_key_file': self.certificate.client_key_file,
                'client_cert_data': self.certificate.client_cert_data,
                'client_key_data': self.certificate.client_key_data,
                'check_hostname': self.certificate.check_hostname,
                'cert_reqs': self.certificate.cert_reqs,
                'ssl_version': self.certificate.ssl_version,
                'ciphers': self.certificate.ciphers,
                'cert_verify_mode': self.certificate.cert_verify_mode
            },
            'headers': self.headers,
            'verify_ssl': self.verify_ssl,
            'follow_redirects': self.follow_redirects
        }
