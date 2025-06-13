"""Tests for the list_dimensions module."""

import json
import pytest
from unittest.mock import patch, Mock

from src.tools.metricflow.list_dimensions import list_dimensions
from src.config.config import MfCliConfig


class TestListDimensions:
    """Test cases for list_dimensions function."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock MfCliConfig for testing."""
        return MfCliConfig(
            project_dir="/test/project",
            profiles_dir="/test/profiles",
            mf_path="/usr/bin/mf",
            tmp_dir="/tmp/metricflow"
        )

    @patch('src.tools.metricflow.list_dimensions.run_mf_command')
    def test_list_dimensions_basic(self, mock_run_command, mock_config):
        """Test basic list dimensions without any parameters."""
        # Mock command output
        mock_output = "customer_id\ndate\nregion\ncategory"
        mock_run_command.return_value = (mock_output, None)

        # Run list dimensions
        result_json, stdout = list_dimensions(mock_config)

        # Verify command was called correctly
        mock_run_command.assert_called_once_with(["list", "dimensions"], mock_config)

        # Verify output
        assert stdout == mock_output

        # Verify JSON output
        result_dict = json.loads(result_json)
        assert result_dict["info"] == mock_output
        assert result_dict["error"] is None

    @patch('src.tools.metricflow.list_dimensions.run_mf_command')
    def test_list_dimensions_with_single_metric(self, mock_run_command, mock_config):
        """Test list dimensions with single metric parameter."""
        # Mock command output
        mock_output = "customer_id\ndate\nregion"
        mock_run_command.return_value = (mock_output, None)

        # Run list dimensions with single metric
        result_json, stdout = list_dimensions(mock_config, metrics=["revenue"])

        # Verify command was called with metrics parameter
        mock_run_command.assert_called_once_with(
            ["list", "dimensions", "--metrics", "revenue"],
            mock_config
        )

        # Verify output
        assert stdout == mock_output
        result_dict = json.loads(result_json)
        assert result_dict["info"] == mock_output

    @patch('src.tools.metricflow.list_dimensions.run_mf_command')
    def test_list_dimensions_with_multiple_metrics(self, mock_run_command, mock_config):
        """Test list dimensions with multiple metrics."""
        # Mock command output
        mock_output = "customer_id\ndate\nregion\nproduct_id"
        mock_run_command.return_value = (mock_output, None)

        # Run list dimensions with multiple metrics
        result_json, stdout = list_dimensions(
            mock_config,
            metrics=["revenue", "orders", "profit"]
        )

        # Verify command was called with comma-separated metrics
        mock_run_command.assert_called_once_with(
            ["list", "dimensions", "--metrics", "revenue,orders,profit"],
            mock_config
        )

        # Verify output
        assert stdout == mock_output

    @patch('src.tools.metricflow.list_dimensions.run_mf_command')
    def test_list_dimensions_with_empty_metrics_list(self, mock_run_command, mock_config):
        """Test list dimensions with empty metrics list."""
        # Mock command output
        mock_output = "All dimensions"
        mock_run_command.return_value = (mock_output, None)

        # Run list dimensions with empty metrics list
        result_json, stdout = list_dimensions(mock_config, metrics=[])

        # Verify command was called without metrics parameter when empty list
        mock_run_command.assert_called_once_with(
            ["list", "dimensions"],
            mock_config
        )

    @patch('src.tools.metricflow.list_dimensions.run_mf_command')
    def test_list_dimensions_with_error(self, mock_run_command, mock_config):
        """Test list dimensions with error output."""
        # Mock command output with error
        mock_run_command.return_value = ("", "Error: Invalid metric name")

        # Run list dimensions
        result_json, stdout = list_dimensions(mock_config, metrics=["invalid_metric"])

        # Verify output
        assert stdout == ""

        # Verify JSON output includes error
        result_dict = json.loads(result_json)
        assert result_dict["info"] == ""
        assert result_dict["error"] == "Error: Invalid metric name"

    @patch('src.tools.metricflow.list_dimensions.run_mf_command')
    def test_list_dimensions_no_metrics_parameter(self, mock_run_command, mock_config):
        """Test that missing metrics parameter is handled correctly."""
        # Mock command output
        mock_output = "All dimensions listed"
        mock_run_command.return_value = (mock_output, None)

        # Run list dimensions without metrics parameter
        result_json, stdout = list_dimensions(mock_config)

        # Verify command was called without metrics
        mock_run_command.assert_called_once_with(["list", "dimensions"], mock_config)

    @patch('src.tools.metricflow.list_dimensions.run_mf_command')
    def test_list_dimensions_metrics_with_special_characters(self, mock_run_command, mock_config):
        """Test list dimensions with metrics containing special characters."""
        # Mock command output
        mock_output = "dim1\ndim2"
        mock_run_command.return_value = (mock_output, None)

        # Run list dimensions with special character metrics
        result_json, stdout = list_dimensions(
            mock_config,
            metrics=["metric_with_underscore", "metric-with-dash", "metric.with.dot"]
        )

        # Verify metrics are joined correctly
        mock_run_command.assert_called_once_with(
            ["list", "dimensions", "--metrics", "metric_with_underscore,metric-with-dash,metric.with.dot"],
            mock_config
        )

    @patch('src.tools.metricflow.list_dimensions.run_mf_command')
    def test_list_dimensions_ignored_parameters(self, mock_run_command, mock_config):
        """Test that unexpected parameters are ignored."""
        # Mock command output
        mock_output = "dimensions"
        mock_run_command.return_value = (mock_output, None)

        # Run list dimensions with extra parameters
        result_json, stdout = list_dimensions(
            mock_config,
            metrics=["test"],
            unknown_param="ignored",
            another_param=123
        )

        # Verify only valid parameters were used
        mock_run_command.assert_called_once_with(
            ["list", "dimensions", "--metrics", "test"],
            mock_config
        )
