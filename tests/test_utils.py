"""
Unit tests for the utils module.
"""

import pytest
import json
from unittest.mock import Mock
from http_service.utils import (
    build_url, sanitize_headers, format_request_log, format_response_log,
    is_retryable_status_code, is_retryable_exception, merge_headers,
    create_auth_header, extract_rate_limit_info, calculate_backoff_delay,
    is_url_absolute, normalize_url, get_content_type, parse_json_response,
    validate_response
)


class TestBuildUrl:
    """Test build_url function."""
    
    def test_build_url_with_base_and_path(self):
        """Test build_url with base URL and path."""
        result = build_url("https://api.example.com", "/users")
        assert result == "https://api.example.com/users"
    
    def test_build_url_with_base_and_path_no_slash(self):
        """Test build_url with base URL and path without leading slash."""
        result = build_url("https://api.example.com", "users")
        assert result == "https://api.example.com/users"
    
    def test_build_url_with_base_ending_slash(self):
        """Test build_url with base URL ending with slash."""
        result = build_url("https://api.example.com/", "/users")
        assert result == "https://api.example.com/users"
    
    def test_build_url_with_params(self):
        """Test build_url with query parameters."""
        result = build_url("https://api.example.com", "/users", {"page": 1, "limit": 10})
        assert result == "https://api.example.com/users?page=1&limit=10"
    
    def test_build_url_with_existing_params(self):
        """Test build_url with URL that already has parameters."""
        result = build_url("https://api.example.com/users?existing=1", "", {"page": 1})
        assert result == "https://api.example.com/users?existing=1&page=1"
    
    def test_build_url_absolute_url(self):
        """Test build_url with absolute URL (should return as-is)."""
        result = build_url("https://api.example.com", "https://other.example.com/users")
        assert result == "https://other.example.com/users"
    
    def test_build_url_no_base(self):
        """Test build_url with no base URL."""
        result = build_url(None, "/users")
        assert result == "/users"
    
    def test_build_url_empty_path(self):
        """Test build_url with empty path."""
        result = build_url("https://api.example.com", "")
        assert result == "https://api.example.com"


class TestSanitizeHeaders:
    """Test sanitize_headers function."""
    
    def test_sanitize_headers_with_sensitive_headers(self):
        """Test sanitize_headers with sensitive headers."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer secret-token",
            "X-API-Key": "secret-api-key",
            "User-Agent": "TestClient/1.0"
        }
        sensitive_headers = ["authorization", "x-api-key"]
        
        result = sanitize_headers(headers, sensitive_headers)
        
        assert result["Content-Type"] == "application/json"
        assert result["Authorization"] == "[REDACTED]"
        assert result["X-API-Key"] == "[REDACTED]"
        assert result["User-Agent"] == "TestClient/1.0"
    
    def test_sanitize_headers_case_insensitive(self):
        """Test sanitize_headers with case insensitive matching."""
        headers = {
            "AUTHORIZATION": "Bearer secret-token",
            "x-api-key": "secret-api-key"
        }
        sensitive_headers = ["authorization", "X-API-Key"]
        
        result = sanitize_headers(headers, sensitive_headers)
        
        assert result["AUTHORIZATION"] == "[REDACTED]"
        assert result["x-api-key"] == "[REDACTED]"
    
    def test_sanitize_headers_no_sensitive_headers(self):
        """Test sanitize_headers with no sensitive headers."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "TestClient/1.0"
        }
        sensitive_headers = ["authorization", "x-api-key"]
        
        result = sanitize_headers(headers, sensitive_headers)
        
        assert result == headers
    
    def test_sanitize_headers_empty_headers(self):
        """Test sanitize_headers with empty headers."""
        result = sanitize_headers({}, ["authorization"])
        assert result == {}


class TestFormatRequestLog:
    """Test format_request_log function."""
    
    def test_format_request_log_basic(self):
        """Test format_request_log with basic request."""
        request = Mock()
        request.method = "GET"
        request.url = "https://api.example.com/users"
        request.headers = {"Content-Type": "application/json"}
        
        result = format_request_log(request)
        
        assert "GET" in result
        assert "https://api.example.com/users" in result
        assert "Content-Type" in result
    
    def test_format_request_log_with_body(self):
        """Test format_request_log with request body."""
        request = Mock()
        request.method = "POST"
        request.url = "https://api.example.com/users"
        request.headers = {"Content-Type": "application/json"}
        request.content = b'{"name": "test"}'
        
        result = format_request_log(request)
        
        assert "POST" in result
        assert "https://api.example.com/users" in result
        assert "name" in result


class TestFormatResponseLog:
    """Test format_response_log function."""
    
    def test_format_response_log_basic(self):
        """Test format_response_log with basic response."""
        response = Mock()
        response.status_code = 200
        response.reason_phrase = "OK"
        response.headers = {"Content-Type": "application/json"}
        response.content = b'{"message": "success"}'
        
        result = format_response_log(response)
        
        assert "200" in result
        assert "OK" in result
        assert "Content-Type" in result
        assert "message" in result
    
    def test_format_response_log_error(self):
        """Test format_response_log with error response."""
        response = Mock()
        response.status_code = 500
        response.reason_phrase = "Internal Server Error"
        response.headers = {"Content-Type": "application/json"}
        response.content = b'{"error": "server error"}'
        
        result = format_response_log(response)
        
        assert "500" in result
        assert "Internal Server Error" in result
        assert "error" in result


class TestIsRetryableStatusCode:
    """Test is_retryable_status_code function."""
    
    def test_is_retryable_status_code_retryable(self):
        """Test is_retryable_status_code with retryable status codes."""
        retryable_codes = [429, 500, 502, 503, 504]
        
        for code in retryable_codes:
            assert is_retryable_status_code(code, retryable_codes) is True
    
    def test_is_retryable_status_code_not_retryable(self):
        """Test is_retryable_status_code with non-retryable status codes."""
        retryable_codes = [429, 500, 502, 503, 504]
        non_retryable_codes = [200, 201, 400, 401, 403, 404]
        
        for code in non_retryable_codes:
            assert is_retryable_status_code(code, retryable_codes) is False
    
    def test_is_retryable_status_code_empty_list(self):
        """Test is_retryable_status_code with empty retryable codes list."""
        assert is_retryable_status_code(500, []) is False


class TestIsRetryableException:
    """Test is_retryable_exception function."""
    
    def test_is_retryable_exception_retryable(self):
        """Test is_retryable_exception with retryable exceptions."""
        import httpx
        
        retryable_exceptions = [httpx.ConnectTimeout, httpx.ReadTimeout]
        
        assert is_retryable_exception(httpx.ConnectTimeout("timeout"), retryable_exceptions) is True
        assert is_retryable_exception(httpx.ReadTimeout("timeout"), retryable_exceptions) is True
    
    def test_is_retryable_exception_not_retryable(self):
        """Test is_retryable_exception with non-retryable exceptions."""
        import httpx
        
        retryable_exceptions = [httpx.ConnectTimeout, httpx.ReadTimeout]
        
        assert is_retryable_exception(ValueError("value error"), retryable_exceptions) is False
        assert is_retryable_exception(httpx.HTTPStatusError("status error", request=Mock(), response=Mock()), retryable_exceptions) is False
    
    def test_is_retryable_exception_empty_list(self):
        """Test is_retryable_exception with empty retryable exceptions list."""
        assert is_retryable_exception(ValueError("error"), []) is False


class TestMergeHeaders:
    """Test merge_headers function."""
    
    def test_merge_headers_basic(self):
        """Test merge_headers with basic headers."""
        headers1 = {"Content-Type": "application/json"}
        headers2 = {"Authorization": "Bearer token"}
        
        result = merge_headers(headers1, headers2)
        
        assert result["Content-Type"] == "application/json"
        assert result["Authorization"] == "Bearer token"
    
    def test_merge_headers_override(self):
        """Test merge_headers with header override."""
        headers1 = {"Content-Type": "application/json", "User-Agent": "Client1"}
        headers2 = {"Content-Type": "text/plain", "Authorization": "Bearer token"}
        
        result = merge_headers(headers1, headers2)
        
        assert result["Content-Type"] == "text/plain"  # headers2 overrides headers1
        assert result["User-Agent"] == "Client1"
        assert result["Authorization"] == "Bearer token"
    
    def test_merge_headers_empty(self):
        """Test merge_headers with empty headers."""
        result = merge_headers({}, {})
        assert result == {}
        
        result = merge_headers({"Content-Type": "application/json"}, {})
        assert result == {"Content-Type": "application/json"}
        
        result = merge_headers({}, {"Authorization": "Bearer token"})
        assert result == {"Authorization": "Bearer token"}


class TestCreateAuthHeader:
    """Test create_auth_header function."""
    
    def test_create_auth_header_basic(self):
        """Test create_auth_header with basic auth."""
        auth_config = Mock()
        auth_config.auth_type = "basic"
        auth_config.username = "testuser"
        auth_config.password = "testpass"
        
        result = create_auth_header(auth_config)
        
        assert result == {"Authorization": "Basic dGVzdHVzZXI6dGVzdHBhc3M="}
    
    def test_create_auth_header_bearer(self):
        """Test create_auth_header with bearer token."""
        auth_config = Mock()
        auth_config.auth_type = "bearer"
        auth_config.token = "test-token"
        
        result = create_auth_header(auth_config)
        
        assert result == {"Authorization": "Bearer test-token"}
    
    def test_create_auth_header_api_key(self):
        """Test create_auth_header with API key."""
        auth_config = Mock()
        auth_config.auth_type = "api_key"
        auth_config.api_key = "test-api-key"
        auth_config.api_key_header = "X-API-Key"
        
        result = create_auth_header(auth_config)
        
        assert result == {"X-API-Key": "test-api-key"}
    
    def test_create_auth_header_none(self):
        """Test create_auth_header with no auth."""
        auth_config = Mock()
        auth_config.auth_type = "none"
        
        result = create_auth_header(auth_config)
        
        assert result == {}
    
    def test_create_auth_header_invalid_type(self):
        """Test create_auth_header with invalid auth type."""
        auth_config = Mock()
        auth_config.auth_type = "invalid"
        
        result = create_auth_header(auth_config)
        
        assert result == {}


class TestExtractRateLimitInfo:
    """Test extract_rate_limit_info function."""
    
    def test_extract_rate_limit_info_with_headers(self):
        """Test extract_rate_limit_info with rate limit headers."""
        response = Mock()
        response.headers = {
            "X-RateLimit-Limit": "100",
            "X-RateLimit-Remaining": "95",
            "X-RateLimit-Reset": "1640995200"
        }
        
        result = extract_rate_limit_info(response)
        
        assert result["limit"] == 100
        assert result["remaining"] == 95
        assert result["reset"] == 1640995200
    
    def test_extract_rate_limit_info_missing_headers(self):
        """Test extract_rate_limit_info with missing headers."""
        response = Mock()
        response.headers = {}
        
        result = extract_rate_limit_info(response)
        
        assert result["limit"] is None
        assert result["remaining"] is None
        assert result["reset"] is None
    
    def test_extract_rate_limit_info_invalid_values(self):
        """Test extract_rate_limit_info with invalid header values."""
        response = Mock()
        response.headers = {
            "X-RateLimit-Limit": "invalid",
            "X-RateLimit-Remaining": "invalid",
            "X-RateLimit-Reset": "invalid"
        }
        
        result = extract_rate_limit_info(response)
        
        assert result["limit"] is None
        assert result["remaining"] is None
        assert result["reset"] is None


class TestCalculateBackoffDelay:
    """Test calculate_backoff_delay function."""
    
    def test_calculate_backoff_delay_first_attempt(self):
        """Test calculate_backoff_delay for first attempt."""
        result = calculate_backoff_delay(1, 1.0, 2.0)
        assert result == 1.0
    
    def test_calculate_backoff_delay_second_attempt(self):
        """Test calculate_backoff_delay for second attempt."""
        result = calculate_backoff_delay(2, 1.0, 2.0)
        assert result == 2.0
    
    def test_calculate_backoff_delay_third_attempt(self):
        """Test calculate_backoff_delay for third attempt."""
        result = calculate_backoff_delay(3, 1.0, 2.0)
        assert result == 4.0
    
    def test_calculate_backoff_delay_with_jitter(self):
        """Test calculate_backoff_delay with jitter."""
        result = calculate_backoff_delay(2, 1.0, 2.0, jitter=True)
        # Should be between 1.0 and 2.0
        assert 1.0 <= result <= 2.0


class TestIsUrlAbsolute:
    """Test is_url_absolute function."""
    
    def test_is_url_absolute_true(self):
        """Test is_url_absolute with absolute URLs."""
        assert is_url_absolute("https://api.example.com/users") is True
        assert is_url_absolute("http://localhost:8000/api") is True
        assert is_url_absolute("ftp://example.com/file") is True
    
    def test_is_url_absolute_false(self):
        """Test is_url_absolute with relative URLs."""
        assert is_url_absolute("/users") is False
        assert is_url_absolute("users") is False
        assert is_url_absolute("?page=1") is False
        assert is_url_absolute("#section") is False


class TestNormalizeUrl:
    """Test normalize_url function."""
    
    def test_normalize_url_absolute(self):
        """Test normalize_url with absolute URL."""
        result = normalize_url("https://api.example.com/users")
        assert result == "https://api.example.com/users"
    
    def test_normalize_url_relative(self):
        """Test normalize_url with relative URL."""
        result = normalize_url("/users")
        assert result == "/users"
    
    def test_normalize_url_with_params(self):
        """Test normalize_url with URL containing parameters."""
        result = normalize_url("https://api.example.com/users?page=1&limit=10")
        assert result == "https://api.example.com/users?page=1&limit=10"


class TestGetContentType:
    """Test get_content_type function."""
    
    def test_get_content_type_from_headers(self):
        """Test get_content_type with content-type in headers."""
        headers = {"Content-Type": "application/json; charset=utf-8"}
        result = get_content_type(headers)
        assert result == "application/json"
    
    def test_get_content_type_missing(self):
        """Test get_content_type with missing content-type."""
        headers = {}
        result = get_content_type(headers)
        assert result is None
    
    def test_get_content_type_without_charset(self):
        """Test get_content_type without charset."""
        headers = {"Content-Type": "application/json"}
        result = get_content_type(headers)
        assert result == "application/json"


class TestParseJsonResponse:
    """Test parse_json_response function."""
    
    def test_parse_json_response_valid(self):
        """Test parse_json_response with valid JSON."""
        response = Mock()
        response.json.return_value = {"message": "success"}
        
        result = parse_json_response(response)
        
        assert result == {"message": "success"}
        response.json.assert_called_once()
    
    def test_parse_json_response_invalid_json(self):
        """Test parse_json_response with invalid JSON."""
        response = Mock()
        response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        
        with pytest.raises(json.JSONDecodeError):
            parse_json_response(response)


class TestValidateResponse:
    """Test validate_response function."""
    
    def test_validate_response_success(self):
        """Test validate_response with successful response."""
        response = Mock()
        response.status_code = 200
        response.raise_for_status.return_value = None
        
        # Should not raise an exception
        validate_response(response)
        response.raise_for_status.assert_called_once()
    
    def test_validate_response_error(self):
        """Test validate_response with error response."""
        import httpx
        
        response = Mock()
        response.status_code = 500
        response.raise_for_status.side_effect = httpx.HTTPStatusError("HTTP 500", request=Mock(), response=response)
        
        with pytest.raises(httpx.HTTPStatusError):
            validate_response(response)
