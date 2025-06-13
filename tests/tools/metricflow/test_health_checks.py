"""Tests for the health_checks module."""

import json
import pytest
from unittest.mock import patch, Mock

from src.tools.metricflow.health_checks import health_checks
from src.config.config import MfCliConfig


class TestHealthChecks:
    """Test cases for health_checks function."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock MfCliConfig for testing."""
        return MfCliConfig(
            project_dir="/test/project",
            profiles_dir="/test/profiles",
            mf_path="/usr/bin/mf",
            tmp_dir="/tmp/metricflow"
        )

    @patch('src.tools.metricflow.health_checks.run_mf_command')
    def test_health_checks_success(self, mock_run_command, mock_config):
        """Test successful health checks execution."""
        # Mock successful command output
        mock_run_command.return_value = ("Health checks passed", None)

        # Run health checks
        result_json, stdout = health_checks(mock_config)

        # Verify command was called correctly
        mock_run_command.assert_called_once_with(["health-checks"], mock_config)

        # Verify output
        assert stdout == "Health checks passed"

        # Verify JSON output
        result_dict = json.loads(result_json)
        assert result_dict["info"] == "Health checks passed"
        assert result_dict["error"] is None

    @patch('src.tools.metricflow.health_checks.run_mf_command')
    def test_health_checks_with_error(self, mock_run_command, mock_config):
        """Test health checks with error output."""
        # Mock command output with error
        mock_run_command.return_value = ("Partial output", "Connection error")

        # Run health checks
        result_json, stdout = health_checks(mock_config)

        # Verify command was called correctly
        mock_run_command.assert_called_once_with(["health-checks"], mock_config)

        # Verify output
        assert stdout == "Partial output"

        # Verify JSON output includes error
        result_dict = json.loads(result_json)
        assert result_dict["info"] == "Partial output"
        assert result_dict["error"] == "Connection error"

    @patch('src.tools.metricflow.health_checks.run_mf_command')
    def test_health_checks_empty_output(self, mock_run_command, mock_config):
        """Test health checks with empty output."""
        # Mock empty command output
        mock_run_command.return_value = ("", "")

        # Run health checks
        result_json, stdout = health_checks(mock_config)

        # Verify command was called correctly
        mock_run_command.assert_called_once_with(["health-checks"], mock_config)

        # Verify output
        assert stdout == ""

        # Verify JSON output
        result_dict = json.loads(result_json)
        assert result_dict["info"] == ""
        assert result_dict["error"] == ""

    @patch('src.tools.metricflow.health_checks.run_mf_command')
    def test_health_checks_complex_output(self, mock_run_command, mock_config):
        """Test health checks with complex multi-line output."""
        # Mock complex output
        complex_output = """Running health checks...
✓ Database connection: OK
✓ Schema validation: OK
✓ Metrics validation: OK
All health checks passed!"""

        mock_run_command.return_value = (complex_output, None)

        # Run health checks
        result_json, stdout = health_checks(mock_config)

        # Verify output
        assert stdout == complex_output

        # Verify JSON output preserves formatting
        result_dict = json.loads(result_json)
        assert result_dict["info"] == complex_output
        assert result_dict["error"] is None

    @patch('src.tools.metricflow.health_checks.run_mf_command')
    def test_health_checks_json_special_characters(self, mock_run_command, mock_config):
        """Test health checks with output containing JSON special characters."""
        # Mock output with special characters
        special_output = 'Health check "test" with \\backslash and \nnewline'

        mock_run_command.return_value = (special_output, None)

        # Run health checks
        result_json, stdout = health_checks(mock_config)

        # Verify JSON is valid and properly escaped
        result_dict = json.loads(result_json)
        assert result_dict["info"] == special_output
        assert result_dict["error"] is None
