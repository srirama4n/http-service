"""
Configuration module for HTTP client settings.
Loads configuration from environment variables and .env file.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class HTTPClientConfig:
    """Configuration for HTTP client settings."""
    
    # Base settings
    base_url: Optional[str] = None
    verify_ssl: bool = True
    enable_logging: bool = True
    
    # Timeout settings
    connect_timeout: float = 10.0
    read_timeout: float = 30.0
    write_timeout: float = 30.0
    pool_timeout: float = 10.0
    
    # Connection pool settings
    max_connections: int = 10
    max_keepalive_connections: int = 5
    keepalive_expiry: float = 30.0
    
    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0
    backoff_factor: float = 2.0
    retry_on_status_codes: list = field(default_factory=lambda: [429, 500, 502, 503, 504])
    
    # Rate limiting
    rate_limit_requests_per_second: Optional[float] = None
    
    # Circuit breaker settings
    circuit_breaker_enabled: bool = False
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout: float = 60.0
    circuit_breaker_failure_status_codes: list = field(default_factory=lambda: [500, 502, 503, 504])
    circuit_breaker_success_threshold: int = 2
    
    # Authentication settings
    auth_type: str = "none"  # "none", "basic", "bearer", "api_key"
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    api_key: Optional[str] = None
    api_key_header: str = "X-API-Key"
    
    # Certificate settings
    ca_cert_file: Optional[str] = None
    ca_cert_data: Optional[str] = None
    client_cert_file: Optional[str] = None
    client_key_file: Optional[str] = None
    client_cert_data: Optional[str] = None
    client_key_data: Optional[str] = None
    check_hostname: bool = True
    cert_reqs: str = "CERT_REQUIRED"
    ssl_version: Optional[str] = None
    ciphers: Optional[str] = None
    cert_verify_mode: Optional[str] = None
    
    # Custom headers
    custom_headers: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def from_env(cls) -> 'HTTPClientConfig':
        """Create configuration from environment variables."""
        return cls(
            # Base settings
            base_url=os.getenv('HTTP_BASE_URL'),
            verify_ssl=os.getenv('HTTP_VERIFY_SSL', 'true').lower() == 'true',
            enable_logging=os.getenv('HTTP_ENABLE_LOGGING', 'true').lower() == 'true',
            
            # Timeout settings
            connect_timeout=float(os.getenv('HTTP_CONNECT_TIMEOUT', '10.0')),
            read_timeout=float(os.getenv('HTTP_READ_TIMEOUT', '30.0')),
            write_timeout=float(os.getenv('HTTP_WRITE_TIMEOUT', '30.0')),
            pool_timeout=float(os.getenv('HTTP_POOL_TIMEOUT', '10.0')),
            
            # Connection pool settings
            max_connections=int(os.getenv('HTTP_MAX_CONNECTIONS', '10')),
            max_keepalive_connections=int(os.getenv('HTTP_MAX_KEEPALIVE_CONNECTIONS', '5')),
            keepalive_expiry=float(os.getenv('HTTP_KEEPALIVE_EXPIRY', '30.0')),
            
            # Retry settings
            max_retries=int(os.getenv('HTTP_MAX_RETRIES', '3')),
            retry_delay=float(os.getenv('HTTP_RETRY_DELAY', '1.0')),
            backoff_factor=float(os.getenv('HTTP_BACKOFF_FACTOR', '2.0')),
            retry_on_status_codes=[
                int(code.strip()) 
                for code in os.getenv('HTTP_RETRY_STATUS_CODES', '429,500,502,503,504').split(',')
            ],
            
            # Rate limiting
            rate_limit_requests_per_second=float(os.getenv('HTTP_RATE_LIMIT_RPS')) if os.getenv('HTTP_RATE_LIMIT_RPS') else None,
            
            # Circuit breaker settings
            circuit_breaker_enabled=os.getenv('HTTP_CIRCUIT_BREAKER_ENABLED', 'false').lower() == 'true',
            circuit_breaker_failure_threshold=int(os.getenv('HTTP_CIRCUIT_BREAKER_FAILURE_THRESHOLD', '5')),
            circuit_breaker_recovery_timeout=float(os.getenv('HTTP_CIRCUIT_BREAKER_RECOVERY_TIMEOUT', '60.0')),
            circuit_breaker_failure_status_codes=[
                int(code.strip()) 
                for code in os.getenv('HTTP_CIRCUIT_BREAKER_FAILURE_STATUS_CODES', '500,502,503,504').split(',')
            ],
            circuit_breaker_success_threshold=int(os.getenv('HTTP_CIRCUIT_BREAKER_SUCCESS_THRESHOLD', '2')),
            
            # Authentication settings
            auth_type=os.getenv('HTTP_AUTH_TYPE', 'none'),
            username=os.getenv('HTTP_USERNAME'),
            password=os.getenv('HTTP_PASSWORD'),
            token=os.getenv('HTTP_TOKEN'),
            api_key=os.getenv('HTTP_API_KEY'),
            api_key_header=os.getenv('HTTP_API_KEY_HEADER', 'X-API-Key'),
            
            # Certificate settings
            ca_cert_file=os.getenv('HTTP_CA_CERT_FILE'),
            ca_cert_data=os.getenv('HTTP_CA_CERT_DATA'),
            client_cert_file=os.getenv('HTTP_CLIENT_CERT_FILE'),
            client_key_file=os.getenv('HTTP_CLIENT_KEY_FILE'),
            client_cert_data=os.getenv('HTTP_CLIENT_CERT_DATA'),
            client_key_data=os.getenv('HTTP_CLIENT_KEY_DATA'),
            check_hostname=os.getenv('HTTP_CHECK_HOSTNAME', 'true').lower() == 'true',
            cert_reqs=os.getenv('HTTP_CERT_REQS', 'CERT_REQUIRED'),
            ssl_version=os.getenv('HTTP_SSL_VERSION'),
            ciphers=os.getenv('HTTP_CIPHERS'),
            cert_verify_mode=os.getenv('HTTP_CERT_VERIFY_MODE'),
            
            # Custom headers
            custom_headers=cls._parse_custom_headers()
        )
    
    @staticmethod
    def _parse_custom_headers() -> Dict[str, str]:
        """Parse custom headers from environment variables."""
        headers = {}
        for key, value in os.environ.items():
            if key.startswith('HTTP_HEADER_'):
                header_name = key[12:].replace('_', '-').lower()  # Convert HTTP_HEADER_X_API_KEY to x-api-key
                headers[header_name] = value
        return headers
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'base_url': self.base_url,
            'verify_ssl': self.verify_ssl,
            'enable_logging': self.enable_logging,
            'connect_timeout': self.connect_timeout,
            'read_timeout': self.read_timeout,
            'write_timeout': self.write_timeout,
            'pool_timeout': self.pool_timeout,
            'max_connections': self.max_connections,
            'max_keepalive_connections': self.max_keepalive_connections,
            'keepalive_expiry': self.keepalive_expiry,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'backoff_factor': self.backoff_factor,
            'retry_on_status_codes': self.retry_on_status_codes,
            'rate_limit_requests_per_second': self.rate_limit_requests_per_second,
            'circuit_breaker_enabled': self.circuit_breaker_enabled,
            'circuit_breaker_failure_threshold': self.circuit_breaker_failure_threshold,
            'circuit_breaker_recovery_timeout': self.circuit_breaker_recovery_timeout,
            'circuit_breaker_failure_status_codes': self.circuit_breaker_failure_status_codes,
            'circuit_breaker_success_threshold': self.circuit_breaker_success_threshold,
            'auth_type': self.auth_type,
            'username': self.username,
            'password': self.password,
            'token': self.token,
            'api_key': self.api_key,
            'api_key_header': self.api_key_header,
            'ca_cert_file': self.ca_cert_file,
            'ca_cert_data': self.ca_cert_data,
            'client_cert_file': self.client_cert_file,
            'client_key_file': self.client_key_file,
            'client_cert_data': self.client_cert_data,
            'client_key_data': self.client_key_data,
            'check_hostname': self.check_hostname,
            'cert_reqs': self.cert_reqs,
            'ssl_version': self.ssl_version,
            'ciphers': self.ciphers,
            'cert_verify_mode': self.cert_verify_mode,
            'custom_headers': self.custom_headers
        }


def get_config() -> HTTPClientConfig:
    """Get the default configuration from environment variables."""
    return HTTPClientConfig.from_env()


def get_config_for_service(service_name: str) -> HTTPClientConfig:
    """Get configuration for a specific service with prefixed environment variables."""
    prefix = f"{service_name.upper()}_"
    
    config = HTTPClientConfig.from_env()
    
    # Base settings
    config.base_url = os.getenv(f'{prefix}BASE_URL', config.base_url)
    config.verify_ssl = os.getenv(f'{prefix}VERIFY_SSL', str(config.verify_ssl)).lower() == 'true'
    config.enable_logging = os.getenv(f'{prefix}ENABLE_LOGGING', str(config.enable_logging)).lower() == 'true'
    
    # Timeout settings
    config.connect_timeout = float(os.getenv(f'{prefix}CONNECT_TIMEOUT', str(config.connect_timeout)))
    config.read_timeout = float(os.getenv(f'{prefix}READ_TIMEOUT', str(config.read_timeout)))
    config.write_timeout = float(os.getenv(f'{prefix}WRITE_TIMEOUT', str(config.write_timeout)))
    config.pool_timeout = float(os.getenv(f'{prefix}POOL_TIMEOUT', str(config.pool_timeout)))
    
    # Connection pool settings
    config.max_connections = int(os.getenv(f'{prefix}MAX_CONNECTIONS', str(config.max_connections)))
    config.max_keepalive_connections = int(os.getenv(f'{prefix}MAX_KEEPALIVE_CONNECTIONS', str(config.max_keepalive_connections)))
    config.keepalive_expiry = float(os.getenv(f'{prefix}KEEPALIVE_EXPIRY', str(config.keepalive_expiry)))
    
    # Retry settings
    config.max_retries = int(os.getenv(f'{prefix}MAX_RETRIES', str(config.max_retries)))
    config.retry_delay = float(os.getenv(f'{prefix}RETRY_DELAY', str(config.retry_delay)))
    config.backoff_factor = float(os.getenv(f'{prefix}BACKOFF_FACTOR', str(config.backoff_factor)))
    
    # Handle retry status codes with default fallback
    retry_codes_env = os.getenv(f'{prefix}RETRY_STATUS_CODES')
    if retry_codes_env:
        config.retry_on_status_codes = [
            int(code.strip()) 
            for code in retry_codes_env.split(',')
        ]
    
    # Rate limiting
    rate_limit_env = os.getenv(f'{prefix}RATE_LIMIT_RPS')
    if rate_limit_env:
        config.rate_limit_requests_per_second = float(rate_limit_env)
    
    # Circuit breaker settings
    config.circuit_breaker_enabled = os.getenv(f'{prefix}CIRCUIT_BREAKER_ENABLED', str(config.circuit_breaker_enabled)).lower() == 'true'
    config.circuit_breaker_failure_threshold = int(os.getenv(f'{prefix}CIRCUIT_BREAKER_FAILURE_THRESHOLD', str(config.circuit_breaker_failure_threshold)))
    config.circuit_breaker_recovery_timeout = float(os.getenv(f'{prefix}CIRCUIT_BREAKER_RECOVERY_TIMEOUT', str(config.circuit_breaker_recovery_timeout)))
    config.circuit_breaker_success_threshold = int(os.getenv(f'{prefix}CIRCUIT_BREAKER_SUCCESS_THRESHOLD', str(config.circuit_breaker_success_threshold)))
    
    # Handle circuit breaker failure status codes with default fallback
    cb_failure_codes_env = os.getenv(f'{prefix}CIRCUIT_BREAKER_FAILURE_STATUS_CODES')
    if cb_failure_codes_env:
        config.circuit_breaker_failure_status_codes = [
            int(code.strip()) 
            for code in cb_failure_codes_env.split(',')
        ]
    
    # Authentication settings
    config.auth_type = os.getenv(f'{prefix}AUTH_TYPE', config.auth_type)
    config.api_key = os.getenv(f'{prefix}API_KEY', config.api_key)
    config.api_key_header = os.getenv(f'{prefix}API_KEY_HEADER', config.api_key_header)
    config.token = os.getenv(f'{prefix}TOKEN', config.token)
    config.username = os.getenv(f'{prefix}USERNAME', config.username)
    config.password = os.getenv(f'{prefix}PASSWORD', config.password)
    
    # Auto-detect auth type if not explicitly set
    if config.auth_type == "none":
        if config.api_key:
            config.auth_type = "api_key"
        elif config.token:
            config.auth_type = "bearer"
        elif config.username and config.password:
            config.auth_type = "basic"
    
    # Certificate settings
    config.ca_cert_file = os.getenv(f'{prefix}CA_CERT_FILE', config.ca_cert_file)
    config.ca_cert_data = os.getenv(f'{prefix}CA_CERT_DATA', config.ca_cert_data)
    config.client_cert_file = os.getenv(f'{prefix}CLIENT_CERT_FILE', config.client_cert_file)
    config.client_key_file = os.getenv(f'{prefix}CLIENT_KEY_FILE', config.client_key_file)
    config.client_cert_data = os.getenv(f'{prefix}CLIENT_CERT_DATA', config.client_cert_data)
    config.client_key_data = os.getenv(f'{prefix}CLIENT_KEY_DATA', config.client_key_data)
    config.check_hostname = os.getenv(f'{prefix}CHECK_HOSTNAME', str(config.check_hostname)).lower() == 'true'
    config.cert_reqs = os.getenv(f'{prefix}CERT_REQS', config.cert_reqs)
    config.ssl_version = os.getenv(f'{prefix}SSL_VERSION', config.ssl_version)
    config.ciphers = os.getenv(f'{prefix}CIPHERS', config.ciphers)
    config.cert_verify_mode = os.getenv(f'{prefix}CERT_VERIFY_MODE', config.cert_verify_mode)
    
    # Custom headers
    service_headers = {}
    for key, value in os.environ.items():
        if key.startswith(f'{prefix}HEADER_'):
            header_name = key[len(f'{prefix}HEADER_'):].replace('_', '-').lower()
            service_headers[header_name] = value
    
    if service_headers:
        config.custom_headers.update(service_headers)
    
    return config
