"""Tests for the list_metrics module."""

import json
import pytest
from unittest.mock import patch, Mock

from src.tools.metricflow.list_metrics import list_metrics
from src.config.config import MfCliConfig


class TestListMetrics:
    """Test cases for list_metrics function."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock MfCliConfig for testing."""
        return MfCliConfig(
            project_dir="/test/project",
            profiles_dir="/test/profiles",
            mf_path="/usr/bin/mf",
            tmp_dir="/tmp/metricflow"
        )

    @patch('src.tools.metricflow.list_metrics.run_mf_command')
    def test_list_metrics_basic(self, mock_run_command, mock_config):
        """Test basic list metrics without any parameters."""
        # Mock command output
        mock_output = "metric1\nmetric2\nmetric3"
        mock_run_command.return_value = (mock_output, None)

        # Run list metrics
        result_json, stdout = list_metrics(mock_config)

        # Verify command was called correctly
        mock_run_command.assert_called_once_with(["list", "metrics"], mock_config)

        # Verify output
        assert stdout == mock_output

        # Verify JSON output
        result_dict = json.loads(result_json)
        assert result_dict["info"] == mock_output
        assert result_dict["error"] is None

    @patch('src.tools.metricflow.list_metrics.run_mf_command')
    def test_list_metrics_with_search(self, mock_run_command, mock_config):
        """Test list metrics with search parameter."""
        # Mock command output
        mock_output = "revenue_metric\nrevenue_by_region"
        mock_run_command.return_value = (mock_output, None)

        # Run list metrics with search
        result_json, stdout = list_metrics(mock_config, search="revenue")

        # Verify command was called with search parameter
        mock_run_command.assert_called_once_with(
            ["list", "metrics", "--search", "revenue"],
            mock_config
        )

        # Verify output
        assert stdout == mock_output
        result_dict = json.loads(result_json)
        assert result_dict["info"] == mock_output

    @patch('src.tools.metricflow.list_metrics.run_mf_command')
    def test_list_metrics_with_show_all_dimensions(self, mock_run_command, mock_config):
        """Test list metrics with show_all_dimensions parameter."""
        # Mock command output
        mock_output = "metric1 [dim1, dim2, dim3]\nmetric2 [dim2, dim4]"
        mock_run_command.return_value = (mock_output, None)

        # Run list metrics with show_all_dimensions
        result_json, stdout = list_metrics(mock_config, show_all_dimensions=True)

        # Verify command was called with --show-all-dimensions
        mock_run_command.assert_called_once_with(
            ["list", "metrics", "--show-all-dimensions"],
            mock_config
        )

        # Verify output
        assert stdout == mock_output

    @patch('src.tools.metricflow.list_metrics.run_mf_command')
    def test_list_metrics_with_all_parameters(self, mock_run_command, mock_config):
        """Test list metrics with all parameters."""
        # Mock command output
        mock_output = "revenue_metric [customer_id, region, date]"
        mock_run_command.return_value = (mock_output, None)

        # Run list metrics with all parameters
        result_json, stdout = list_metrics(
            mock_config,
            search="revenue",
            show_all_dimensions=True
        )

        # Verify command was called with all parameters
        mock_run_command.assert_called_once_with(
            ["list", "metrics", "--search", "revenue", "--show-all-dimensions"],
            mock_config
        )

        # Verify output
        assert stdout == mock_output

    @patch('src.tools.metricflow.list_metrics.run_mf_command')
    def test_list_metrics_show_all_dimensions_false(self, mock_run_command, mock_config):
        """Test that show_all_dimensions=False doesn't add the flag."""
        # Mock command output
        mock_output = "metric1\nmetric2"
        mock_run_command.return_value = (mock_output, None)

        # Run list metrics with show_all_dimensions=False
        result_json, stdout = list_metrics(mock_config, show_all_dimensions=False)

        # Verify command was called without --show-all-dimensions
        mock_run_command.assert_called_once_with(["list", "metrics"], mock_config)

    @patch('src.tools.metricflow.list_metrics.run_mf_command')
    def test_list_metrics_with_error(self, mock_run_command, mock_config):
        """Test list metrics with error output."""
        # Mock command output with error
        mock_run_command.return_value = ("", "Error: Connection failed")

        # Run list metrics
        result_json, stdout = list_metrics(mock_config)

        # Verify output
        assert stdout == ""

        # Verify JSON output includes error
        result_dict = json.loads(result_json)
        assert result_dict["info"] == ""
        assert result_dict["error"] == "Error: Connection failed"

    @patch('src.tools.metricflow.list_metrics.run_mf_command')
    def test_list_metrics_empty_search(self, mock_run_command, mock_config):
        """Test list metrics with empty search string."""
        # Mock command output
        mock_output = "All metrics listed"
        mock_run_command.return_value = (mock_output, None)

        # Run list metrics with empty search - empty search should not add search parameter
        result_json, stdout = list_metrics(mock_config, search="")

        # Verify command was called without search parameter when empty (falsy)
        mock_run_command.assert_called_once_with(
            ["list", "metrics"],
            mock_config
        )

    @patch('src.tools.metricflow.list_metrics.run_mf_command')
    def test_list_metrics_ignored_parameters(self, mock_run_command, mock_config):
        """Test that unexpected parameters are ignored."""
        # Mock command output
        mock_output = "metrics"
        mock_run_command.return_value = (mock_output, None)

        # Run list metrics with extra parameters
        result_json, stdout = list_metrics(
            mock_config,
            search="test",
            unknown_param="ignored",
            another_param=123
        )

        # Verify only valid parameters were used
        mock_run_command.assert_called_once_with(
            ["list", "metrics", "--search", "test"],
            mock_config
        )
