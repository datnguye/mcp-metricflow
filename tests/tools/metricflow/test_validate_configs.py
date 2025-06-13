"""Tests for the validate_configs module."""

import json
import pytest
from unittest.mock import patch, Mock

from src.tools.metricflow.validate_configs import validate_configs
from src.config.config import MfCliConfig


class TestValidateConfigs:
    """Test cases for validate_configs function."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock MfCliConfig for testing."""
        return MfCliConfig(
            project_dir="/test/project",
            profiles_dir="/test/profiles",
            mf_path="/usr/bin/mf",
            tmp_dir="/tmp/metricflow"
        )

    @patch('src.tools.metricflow.validate_configs.run_mf_command')
    def test_validate_configs_basic(self, mock_run_command, mock_config):
        """Test basic validate configs without any parameters."""
        # Mock command output
        mock_output = "All configurations are valid"
        mock_run_command.return_value = (mock_output, None)

        # Run validate configs
        result_json, stdout = validate_configs(mock_config)

        # Verify command was called correctly
        mock_run_command.assert_called_once_with(["validate-configs"], mock_config)

        # Verify output
        assert stdout == mock_output

        # Verify JSON output
        result_dict = json.loads(result_json)
        assert result_dict["info"] == mock_output
        assert result_dict["error"] is None

    @patch('src.tools.metricflow.validate_configs.run_mf_command')
    def test_validate_configs_with_dw_timeout(self, mock_run_command, mock_config):
        """Test validate configs with dw_timeout parameter."""
        # Mock command output
        mock_output = "Validation completed with timeout"
        mock_run_command.return_value = (mock_output, None)

        # Run validate configs with dw_timeout
        result_json, stdout = validate_configs(mock_config, dw_timeout=300)

        # Verify command was called with dw_timeout
        mock_run_command.assert_called_once_with(
            ["validate-configs", "--dw-timeout", "300"],
            mock_config
        )

        # Verify output
        assert stdout == mock_output

    @patch('src.tools.metricflow.validate_configs.run_mf_command')
    def test_validate_configs_with_skip_dw(self, mock_run_command, mock_config):
        """Test validate configs with skip_dw flag."""
        # Mock command output
        mock_output = "Validation skipped data warehouse checks"
        mock_run_command.return_value = (mock_output, None)

        # Run validate configs with skip_dw
        result_json, stdout = validate_configs(mock_config, skip_dw=True)

        # Verify command was called with skip_dw flag
        mock_run_command.assert_called_once_with(
            ["validate-configs", "--skip-dw"],
            mock_config
        )

    @patch('src.tools.metricflow.validate_configs.run_mf_command')
    def test_validate_configs_skip_dw_false(self, mock_run_command, mock_config):
        """Test that skip_dw=False doesn't add the flag."""
        # Mock command output
        mock_output = "Validation with DW checks"
        mock_run_command.return_value = (mock_output, None)

        # Run validate configs with skip_dw=False
        result_json, stdout = validate_configs(mock_config, skip_dw=False)

        # Verify command was called without skip_dw flag
        mock_run_command.assert_called_once_with(["validate-configs"], mock_config)

    @patch('src.tools.metricflow.validate_configs.run_mf_command')
    def test_validate_configs_with_show_all(self, mock_run_command, mock_config):
        """Test validate configs with show_all flag."""
        # Mock command output
        mock_output = "Showing all validation results"
        mock_run_command.return_value = (mock_output, None)

        # Run validate configs with show_all
        result_json, stdout = validate_configs(mock_config, show_all=True)

        # Verify command was called with show_all flag
        mock_run_command.assert_called_once_with(
            ["validate-configs", "--show-all"],
            mock_config
        )

    @patch('src.tools.metricflow.validate_configs.run_mf_command')
    def test_validate_configs_with_verbose_issues(self, mock_run_command, mock_config):
        """Test validate configs with verbose_issues flag."""
        # Mock command output
        mock_output = "Verbose issue reporting enabled"
        mock_run_command.return_value = (mock_output, None)

        # Run validate configs with verbose_issues
        result_json, stdout = validate_configs(mock_config, verbose_issues=True)

        # Verify command was called with verbose_issues flag
        mock_run_command.assert_called_once_with(
            ["validate-configs", "--verbose-issues"],
            mock_config
        )

    @patch('src.tools.metricflow.validate_configs.run_mf_command')
    def test_validate_configs_with_semantic_validation_workers(self, mock_run_command, mock_config):
        """Test validate configs with semantic_validation_workers parameter."""
        # Mock command output
        mock_output = "Using 4 semantic validation workers"
        mock_run_command.return_value = (mock_output, None)

        # Run validate configs with semantic_validation_workers
        result_json, stdout = validate_configs(mock_config, semantic_validation_workers=4)

        # Verify command was called with semantic_validation_workers
        mock_run_command.assert_called_once_with(
            ["validate-configs", "--semantic-validation-workers", "4"],
            mock_config
        )

    @patch('src.tools.metricflow.validate_configs.run_mf_command')
    def test_validate_configs_with_all_parameters(self, mock_run_command, mock_config):
        """Test validate configs with all parameters."""
        # Mock command output
        mock_output = "Comprehensive validation completed"
        mock_run_command.return_value = (mock_output, None)

        # Run validate configs with all parameters
        result_json, stdout = validate_configs(
            mock_config,
            dw_timeout=600,
            skip_dw=True,
            show_all=True,
            verbose_issues=True,
            semantic_validation_workers=8
        )

        # Verify command was called with all parameters
        expected_args = [
            "validate-configs",
            "--dw-timeout", "600",
            "--skip-dw",
            "--show-all",
            "--verbose-issues",
            "--semantic-validation-workers", "8"
        ]
        mock_run_command.assert_called_once_with(expected_args, mock_config)

    @patch('src.tools.metricflow.validate_configs.run_mf_command')
    def test_validate_configs_with_error(self, mock_run_command, mock_config):
        """Test validate configs with error output."""
        # Mock command output with error
        mock_run_command.return_value = ("Partial validation", "Configuration errors found")

        # Run validate configs
        result_json, stdout = validate_configs(mock_config)

        # Verify output
        assert stdout == "Partial validation"

        # Verify JSON output includes error
        result_dict = json.loads(result_json)
        assert result_dict["info"] == "Partial validation"
        assert result_dict["error"] == "Configuration errors found"

    @patch('src.tools.metricflow.validate_configs.run_mf_command')
    def test_validate_configs_numeric_parameters_conversion(self, mock_run_command, mock_config):
        """Test that numeric parameters are converted to strings."""
        # Mock command output
        mock_output = "Validation with numeric params"
        mock_run_command.return_value = (mock_output, None)

        # Run validate configs with numeric parameters
        result_json, stdout = validate_configs(
            mock_config,
            dw_timeout=300,
            semantic_validation_workers=2
        )

        # Verify numeric values are converted to strings
        expected_args = [
            "validate-configs",
            "--dw-timeout", "300",
            "--semantic-validation-workers", "2"
        ]
        mock_run_command.assert_called_once_with(expected_args, mock_config)

    @patch('src.tools.metricflow.validate_configs.run_mf_command')
    def test_validate_configs_ignored_parameters(self, mock_run_command, mock_config):
        """Test that unexpected parameters are ignored."""
        # Mock command output
        mock_output = "validation"
        mock_run_command.return_value = (mock_output, None)

        # Run validate configs with extra parameters
        result_json, stdout = validate_configs(
            mock_config,
            show_all=True,
            unknown_param="ignored",
            another_param=123
        )

        # Verify only valid parameters were used
        mock_run_command.assert_called_once_with(
            ["validate-configs", "--show-all"],
            mock_config
        )
