"""Tests for the list_dimension_values module."""

import json
import pytest
from unittest.mock import patch, Mock

from src.tools.metricflow.list_dimension_values import list_dimension_values
from src.config.config import MfCliConfig


class TestListDimensionValues:
    """Test cases for list_dimension_values function."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock MfCliConfig for testing."""
        return MfCliConfig(
            project_dir="/test/project",
            profiles_dir="/test/profiles",
            mf_path="/usr/bin/mf",
            tmp_dir="/tmp/metricflow"
        )

    @patch('src.tools.metricflow.list_dimension_values.run_mf_command')
    def test_list_dimension_values_basic(self, mock_run_command, mock_config):
        """Test basic list dimension values with required parameters."""
        # Mock command output
        mock_output = "value1\nvalue2\nvalue3"
        mock_run_command.return_value = (mock_output, None)

        # Run list dimension values
        result_json, stdout = list_dimension_values(
            mock_config,
            dimension="region",
            metrics=["revenue"]
        )

        # Verify command was called correctly
        mock_run_command.assert_called_once_with(
            ["list", "dimension-values", "--dimension", "region", "--metrics", "revenue"],
            mock_config
        )

        # Verify output
        assert stdout == mock_output

        # Verify JSON output
        result_dict = json.loads(result_json)
        assert result_dict["info"] == mock_output
        assert result_dict["error"] is None

    @patch('src.tools.metricflow.list_dimension_values.run_mf_command')
    def test_list_dimension_values_multiple_metrics(self, mock_run_command, mock_config):
        """Test list dimension values with multiple metrics."""
        # Mock command output
        mock_output = "US\nEU\nASIA"
        mock_run_command.return_value = (mock_output, None)

        # Run list dimension values with multiple metrics
        result_json, stdout = list_dimension_values(
            mock_config,
            dimension="region",
            metrics=["revenue", "orders", "profit"]
        )

        # Verify command was called with comma-separated metrics
        mock_run_command.assert_called_once_with(
            ["list", "dimension-values", "--dimension", "region", "--metrics", "revenue,orders,profit"],
            mock_config
        )

        # Verify output
        assert stdout == mock_output

    @patch('src.tools.metricflow.list_dimension_values.run_mf_command')
    def test_list_dimension_values_with_start_time(self, mock_run_command, mock_config):
        """Test list dimension values with start_time parameter."""
        # Mock command output
        mock_output = "2023-01\n2023-02\n2023-03"
        mock_run_command.return_value = (mock_output, None)

        # Run list dimension values with start_time
        result_json, stdout = list_dimension_values(
            mock_config,
            dimension="date",
            metrics=["revenue"],
            start_time="2023-01-01"
        )

        # Verify command was called with start_time
        mock_run_command.assert_called_once_with(
            ["list", "dimension-values", "--dimension", "date", "--metrics", "revenue", "--start-time", "2023-01-01"],
            mock_config
        )

    @patch('src.tools.metricflow.list_dimension_values.run_mf_command')
    def test_list_dimension_values_with_end_time(self, mock_run_command, mock_config):
        """Test list dimension values with end_time parameter."""
        # Mock command output
        mock_output = "2023-01\n2023-02"
        mock_run_command.return_value = (mock_output, None)

        # Run list dimension values with end_time
        result_json, stdout = list_dimension_values(
            mock_config,
            dimension="date",
            metrics=["revenue"],
            end_time="2023-02-28"
        )

        # Verify command was called with end_time
        mock_run_command.assert_called_once_with(
            ["list", "dimension-values", "--dimension", "date", "--metrics", "revenue", "--end-time", "2023-02-28"],
            mock_config
        )

    @patch('src.tools.metricflow.list_dimension_values.run_mf_command')
    def test_list_dimension_values_with_time_range(self, mock_run_command, mock_config):
        """Test list dimension values with both start_time and end_time."""
        # Mock command output
        mock_output = "2023-01\n2023-02"
        mock_run_command.return_value = (mock_output, None)

        # Run list dimension values with time range
        result_json, stdout = list_dimension_values(
            mock_config,
            dimension="date",
            metrics=["revenue", "orders"],
            start_time="2023-01-01",
            end_time="2023-02-28"
        )

        # Verify command was called with both time parameters
        expected_args = [
            "list", "dimension-values",
            "--dimension", "date",
            "--metrics", "revenue,orders",
            "--start-time", "2023-01-01",
            "--end-time", "2023-02-28"
        ]
        mock_run_command.assert_called_once_with(expected_args, mock_config)

    @patch('src.tools.metricflow.list_dimension_values.run_mf_command')
    def test_list_dimension_values_with_error(self, mock_run_command, mock_config):
        """Test list dimension values with error output."""
        # Mock command output with error
        mock_run_command.return_value = ("", "Error: Invalid dimension")

        # Run list dimension values
        result_json, stdout = list_dimension_values(
            mock_config,
            dimension="invalid_dim",
            metrics=["revenue"]
        )

        # Verify output
        assert stdout == ""

        # Verify JSON output includes error
        result_dict = json.loads(result_json)
        assert result_dict["info"] == ""
        assert result_dict["error"] == "Error: Invalid dimension"

    @patch('src.tools.metricflow.list_dimension_values.run_mf_command')
    def test_list_dimension_values_empty_metrics(self, mock_run_command, mock_config):
        """Test list dimension values with empty metrics list."""
        # Mock command output
        mock_output = "No values"
        mock_run_command.return_value = (mock_output, None)

        # Run list dimension values with empty metrics
        result_json, stdout = list_dimension_values(
            mock_config,
            dimension="region",
            metrics=[]
        )

        # Verify command was called with empty metrics string
        mock_run_command.assert_called_once_with(
            ["list", "dimension-values", "--dimension", "region", "--metrics", ""],
            mock_config
        )

    @patch('src.tools.metricflow.list_dimension_values.run_mf_command')
    def test_list_dimension_values_special_dimension_name(self, mock_run_command, mock_config):
        """Test list dimension values with special characters in dimension name."""
        # Mock command output
        mock_output = "val1\nval2"
        mock_run_command.return_value = (mock_output, None)

        # Run list dimension values with special dimension name
        result_json, stdout = list_dimension_values(
            mock_config,
            dimension="customer_id",
            metrics=["revenue_usd"]
        )

        # Verify command was called correctly
        mock_run_command.assert_called_once_with(
            ["list", "dimension-values", "--dimension", "customer_id", "--metrics", "revenue_usd"],
            mock_config
        )

    @patch('src.tools.metricflow.list_dimension_values.run_mf_command')
    def test_list_dimension_values_ignored_parameters(self, mock_run_command, mock_config):
        """Test that unexpected parameters are ignored."""
        # Mock command output
        mock_output = "values"
        mock_run_command.return_value = (mock_output, None)

        # Run list dimension values with extra parameters
        result_json, stdout = list_dimension_values(
            mock_config,
            dimension="test",
            metrics=["metric1"],
            start_time="2023-01-01",
            unknown_param="ignored",
            another_param=123
        )

        # Verify only valid parameters were used
        expected_args = [
            "list", "dimension-values",
            "--dimension", "test",
            "--metrics", "metric1",
            "--start-time", "2023-01-01"
        ]
        mock_run_command.assert_called_once_with(expected_args, mock_config)
