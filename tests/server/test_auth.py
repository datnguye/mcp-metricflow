"""Tests for the authentication module."""

import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from src.config.config import MfCliConfig
from src.server.auth import verify_api_key


class TestVerifyApiKey:
    """Test cases for verify_api_key function."""

    def test_verify_api_key_auth_not_required(self):
        """Test API key verification when authentication is not required."""
        # Mock request with config that doesn't require auth
        mock_request = Mock()
        mock_config = MfCliConfig(
            project_dir="/test",
            profiles_dir="/test",
            mf_path="test",
            tmp_dir="/test",
            api_key="test-key",
            require_auth=False
        )
        mock_request.app.state.config = mock_config

        # Should return True regardless of credentials
        result = verify_api_key(mock_request, None)
        assert result is True

    def test_verify_api_key_no_config(self):
        """Test API key verification when no config is available."""
        mock_request = Mock()
        mock_request.app.state = Mock(spec=[])  # No config attribute

        with pytest.raises(HTTPException) as exc_info:
            verify_api_key(mock_request, None)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Server configuration not available" in exc_info.value.detail

    def test_verify_api_key_auth_required_no_api_key_configured(self):
        """Test API key verification when auth is required but no API key is configured."""
        mock_request = Mock()
        mock_config = MfCliConfig(
            project_dir="/test",
            profiles_dir="/test",
            mf_path="test",
            tmp_dir="/test",
            api_key=None,
            require_auth=True
        )
        mock_request.app.state.config = mock_config

        with pytest.raises(HTTPException) as exc_info:
            verify_api_key(mock_request, None)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Server authentication not properly configured" in exc_info.value.detail

    def test_verify_api_key_auth_required_no_credentials(self):
        """Test API key verification when auth is required but no credentials provided."""
        mock_request = Mock()
        mock_request.client.host = "127.0.0.1"
        mock_request.headers.get.return_value = "test-agent"
        mock_request.url = "http://test.com/sse"
        mock_config = MfCliConfig(
            project_dir="/test",
            profiles_dir="/test",
            mf_path="test",
            tmp_dir="/test",
            api_key="a" * 32,  # Valid format API key
            require_auth=True
        )
        mock_request.app.state.config = mock_config

        with pytest.raises(HTTPException) as exc_info:
            verify_api_key(mock_request, None)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "API key required"
        assert exc_info.value.headers == {
            "WWW-Authenticate": "Bearer",
            "Cache-Control": "no-store",
            "Pragma": "no-cache"
        }

    def test_verify_api_key_auth_required_invalid_key(self):
        """Test API key verification when auth is required and invalid key is provided."""
        mock_request = Mock()
        mock_request.client.host = "127.0.0.1"
        mock_request.headers.get.return_value = "test-agent"
        mock_request.url = "http://test.com/sse"
        mock_config = MfCliConfig(
            project_dir="/test",
            profiles_dir="/test",
            mf_path="test",
            tmp_dir="/test",
            api_key="a" * 32,  # Valid format API key
            require_auth=True
        )
        mock_request.app.state.config = mock_config

        invalid_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid-key"
        )

        with pytest.raises(HTTPException) as exc_info:
            verify_api_key(mock_request, invalid_credentials)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Invalid API key"
        assert exc_info.value.headers == {
            "WWW-Authenticate": "Bearer",
            "Cache-Control": "no-store",
            "Pragma": "no-cache"
        }

    def test_verify_api_key_auth_required_valid_key(self):
        """Test API key verification when auth is required and valid key is provided."""
        mock_request = Mock()
        mock_config = MfCliConfig(
            project_dir="/test",
            profiles_dir="/test",
            mf_path="test",
            tmp_dir="/test",
            api_key="a" * 32,  # Valid format API key
            require_auth=True
        )
        mock_request.app.state.config = mock_config

        valid_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="a" * 32  # Valid format API key
        )

        result = verify_api_key(mock_request, valid_credentials)
        assert result is True

    def test_verify_api_key_auth_required_empty_key_configured(self):
        """Test API key verification when auth is required but empty key is configured."""
        mock_request = Mock()
        mock_config = MfCliConfig(
            project_dir="/test",
            profiles_dir="/test",
            mf_path="test",
            tmp_dir="/test",
            api_key="",  # Empty string should be treated as None
            require_auth=True
        )
        mock_request.app.state.config = mock_config

        with pytest.raises(HTTPException) as exc_info:
            verify_api_key(mock_request, None)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Server authentication not properly configured" in exc_info.value.detail

    def test_verify_api_key_auth_required_valid_empty_key_match(self):
        """Test API key verification when both configured and provided keys are empty."""
        mock_request = Mock()
        mock_config = MfCliConfig(
            project_dir="/test",
            profiles_dir="/test",
            mf_path="test",
            tmp_dir="/test",
            api_key="",
            require_auth=True
        )
        mock_request.app.state.config = mock_config

        empty_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=""
        )

        # Empty configured key should be treated as no key configured
        with pytest.raises(HTTPException) as exc_info:
            verify_api_key(mock_request, empty_credentials)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_verify_api_key_case_sensitive(self):
        """Test that API key verification is case sensitive."""
        mock_request = Mock()
        mock_config = MfCliConfig(
            project_dir="/test",
            profiles_dir="/test",
            mf_path="test",
            tmp_dir="/test",
            api_key="Valid-Key-123",
            require_auth=True
        )
        mock_request.app.state.config = mock_config

        # Test different case
        wrong_case_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid-key-123"  # Different case
        )

        with pytest.raises(HTTPException) as exc_info:
            verify_api_key(mock_request, wrong_case_credentials)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Invalid API key"

    def test_verify_api_key_special_characters(self):
        """Test API key verification with special characters."""
        special_key = "api-key_with.special+chars@domain.com/path?query=value"

        mock_request = Mock()
        mock_config = MfCliConfig(
            project_dir="/test",
            profiles_dir="/test",
            mf_path="test",
            tmp_dir="/test",
            api_key=special_key,
            require_auth=True
        )
        mock_request.app.state.config = mock_config

        valid_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=special_key
        )

        result = verify_api_key(mock_request, valid_credentials)
        assert result is True

    @patch('src.server.auth.time')
    def test_verify_api_key_rate_limit_exceeded(self, mock_time):
        """Test API key verification when rate limit is exceeded."""
        from src.server.auth import request_counts, MAX_REQUESTS, TIME_WINDOW

        # Clear any existing rate limit data
        request_counts.clear()

        mock_request = Mock()
        mock_request.client.host = "192.168.1.100"
        mock_request.headers.get.return_value = "test-agent"
        mock_request.url = "http://test.com/sse"
        mock_config = MfCliConfig(
            project_dir="/test",
            profiles_dir="/test",
            mf_path="test",
            tmp_dir="/test",
            api_key="a" * 32,
            require_auth=True
        )
        mock_request.app.state.config = mock_config

        # Set up time mock - current time is 1000
        current_time = 1000.0
        mock_time.return_value = current_time

        # Pre-populate with MAX_REQUESTS failed attempts within the time window
        client_ip = "192.168.1.100"
        for _ in range(MAX_REQUESTS):
            request_counts[client_ip].append(current_time - (TIME_WINDOW - 10))  # Recent attempts

        # Now attempt authentication - should trigger rate limit
        with pytest.raises(HTTPException) as exc_info:
            verify_api_key(mock_request, None)

        assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Too many failed authentication attempts" in exc_info.value.detail
        assert exc_info.value.headers == {"Retry-After": str(TIME_WINDOW)}
