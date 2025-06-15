"""Tests for authentication validation functions."""

import pytest
from unittest.mock import Mock

from src.server.auth import validate_api_key_format, validate_auth_config
from src.config.config import MfCliConfig


class TestValidateApiKeyFormat:
    """Test API key format validation."""

    def test_validate_api_key_format_valid_key(self):
        """Test validation with valid API key."""
        valid_key = "a" * 32  # 32 character alphanumeric key
        assert validate_api_key_format(valid_key) is True

    def test_validate_api_key_format_with_hyphens_underscores(self):
        """Test validation with hyphens and underscores."""
        valid_key = "a" * 16 + "-" + "b" * 8 + "_" + "c" * 7
        assert validate_api_key_format(valid_key) is True

    def test_validate_api_key_format_too_short(self):
        """Test validation with too short key."""
        short_key = "a" * 31  # 31 characters - too short
        assert validate_api_key_format(short_key) is False

    def test_validate_api_key_format_empty_key(self):
        """Test validation with empty key."""
        assert validate_api_key_format("") is False
        assert validate_api_key_format(None) is False

    def test_validate_api_key_format_invalid_characters(self):
        """Test validation with invalid characters."""
        invalid_key = "a" * 32 + "!"  # Contains special character
        assert validate_api_key_format(invalid_key) is False

    def test_validate_api_key_format_spaces(self):
        """Test validation with spaces."""
        invalid_key = "a" * 16 + " " + "b" * 16  # Contains space
        assert validate_api_key_format(invalid_key) is False


class TestValidateAuthConfig:
    """Test authentication configuration validation."""

    def test_validate_auth_config_auth_disabled(self):
        """Test validation when auth is disabled."""
        config = MfCliConfig(
            project_dir="/test",
            profiles_dir="/test",
            mf_path="test",
            tmp_dir="/test",
            api_key=None,
            require_auth=False
        )
        # Should not raise any exception
        validate_auth_config(config)

    def test_validate_auth_config_auth_enabled_valid_key(self):
        """Test validation when auth is enabled with valid key."""
        config = MfCliConfig(
            project_dir="/test",
            profiles_dir="/test",
            mf_path="test",
            tmp_dir="/test",
            api_key="a" * 32,  # Valid 32-character key
            require_auth=True
        )
        # Should not raise any exception
        validate_auth_config(config)

    def test_validate_auth_config_auth_enabled_no_key(self):
        """Test validation when auth is enabled but no key provided."""
        config = MfCliConfig(
            project_dir="/test",
            profiles_dir="/test",
            mf_path="test",
            tmp_dir="/test",
            api_key=None,
            require_auth=True
        )
        with pytest.raises(ValueError, match="API key is required when authentication is enabled"):
            validate_auth_config(config)

    def test_validate_auth_config_auth_enabled_invalid_key_format(self):
        """Test validation when auth is enabled but key format is invalid."""
        config = MfCliConfig(
            project_dir="/test",
            profiles_dir="/test",
            mf_path="test",
            tmp_dir="/test",
            api_key="short",  # Too short
            require_auth=True
        )
        with pytest.raises(ValueError, match="API key does not meet security requirements"):
            validate_auth_config(config)

    def test_validate_auth_config_auth_enabled_invalid_key_characters(self):
        """Test validation when auth is enabled but key has invalid characters."""
        config = MfCliConfig(
            project_dir="/test",
            profiles_dir="/test",
            mf_path="test",
            tmp_dir="/test",
            api_key="a" * 32 + "!",  # Invalid character
            require_auth=True
        )
        with pytest.raises(ValueError, match="API key does not meet security requirements"):
            validate_auth_config(config)
