"""Tests for the list_entities module."""

import json
import pytest
from unittest.mock import patch, Mock

from src.tools.metricflow.list_entities import list_entities
from src.config.config import MfCliConfig


class TestListEntities:
    """Test cases for list_entities function."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock MfCliConfig for testing."""
        return MfCliConfig(
            project_dir="/test/project",
            profiles_dir="/test/profiles",
            mf_path="/usr/bin/mf",
            tmp_dir="/tmp/metricflow"
        )

    @patch('src.tools.metricflow.list_entities.run_mf_command')
    def test_list_entities_basic(self, mock_run_command, mock_config):
        """Test basic list entities without any parameters."""
        # Mock command output
        mock_output = "customer\norder\nproduct\nsupplier"
        mock_run_command.return_value = (mock_output, None)

        # Run list entities
        result_json, stdout = list_entities(mock_config)

        # Verify command was called correctly
        mock_run_command.assert_called_once_with(["list", "entities"], mock_config)

        # Verify output
        assert stdout == mock_output

        # Verify JSON output
        result_dict = json.loads(result_json)
        assert result_dict["info"] == mock_output
        assert result_dict["error"] is None

    @patch('src.tools.metricflow.list_entities.run_mf_command')
    def test_list_entities_with_single_metric(self, mock_run_command, mock_config):
        """Test list entities with single metric parameter."""
        # Mock command output
        mock_output = "customer\norder"
        mock_run_command.return_value = (mock_output, None)

        # Run list entities with single metric
        result_json, stdout = list_entities(mock_config, metrics=["revenue"])

        # Verify command was called with metrics parameter
        mock_run_command.assert_called_once_with(
            ["list", "entities", "--metrics", "revenue"],
            mock_config
        )

        # Verify output
        assert stdout == mock_output
        result_dict = json.loads(result_json)
        assert result_dict["info"] == mock_output

    @patch('src.tools.metricflow.list_entities.run_mf_command')
    def test_list_entities_with_multiple_metrics(self, mock_run_command, mock_config):
        """Test list entities with multiple metrics."""
        # Mock command output
        mock_output = "customer\norder\nproduct"
        mock_run_command.return_value = (mock_output, None)

        # Run list entities with multiple metrics
        result_json, stdout = list_entities(
            mock_config,
            metrics=["revenue", "orders", "inventory"]
        )

        # Verify command was called with comma-separated metrics
        mock_run_command.assert_called_once_with(
            ["list", "entities", "--metrics", "revenue,orders,inventory"],
            mock_config
        )

        # Verify output
        assert stdout == mock_output

    @patch('src.tools.metricflow.list_entities.run_mf_command')
    def test_list_entities_with_empty_metrics_list(self, mock_run_command, mock_config):
        """Test list entities with empty metrics list."""
        # Mock command output
        mock_output = "All entities"
        mock_run_command.return_value = (mock_output, None)

        # Run list entities with empty metrics list
        result_json, stdout = list_entities(mock_config, metrics=[])

        # Verify command was called without metrics parameter when empty list
        mock_run_command.assert_called_once_with(
            ["list", "entities"],
            mock_config
        )

    @patch('src.tools.metricflow.list_entities.run_mf_command')
    def test_list_entities_with_error(self, mock_run_command, mock_config):
        """Test list entities with error output."""
        # Mock command output with error
        mock_run_command.return_value = ("", "Error: Metric not found")

        # Run list entities
        result_json, stdout = list_entities(mock_config, metrics=["nonexistent"])

        # Verify output
        assert stdout == ""

        # Verify JSON output includes error
        result_dict = json.loads(result_json)
        assert result_dict["info"] == ""
        assert result_dict["error"] == "Error: Metric not found"

    @patch('src.tools.metricflow.list_entities.run_mf_command')
    def test_list_entities_no_metrics_parameter(self, mock_run_command, mock_config):
        """Test that missing metrics parameter is handled correctly."""
        # Mock command output
        mock_output = "All entities listed"
        mock_run_command.return_value = (mock_output, None)

        # Run list entities without metrics parameter
        result_json, stdout = list_entities(mock_config)

        # Verify command was called without metrics
        mock_run_command.assert_called_once_with(["list", "entities"], mock_config)

    @patch('src.tools.metricflow.list_entities.run_mf_command')
    def test_list_entities_metrics_join_handling(self, mock_run_command, mock_config):
        """Test that metrics are properly joined with commas."""
        # Mock command output
        mock_output = "entity1\nentity2"
        mock_run_command.return_value = (mock_output, None)

        # Run list entities with metrics that need joining
        result_json, stdout = list_entities(
            mock_config,
            metrics=["first_metric", "second_metric", "third_metric"]
        )

        # Verify metrics are joined correctly
        mock_run_command.assert_called_once_with(
            ["list", "entities", "--metrics", "first_metric,second_metric,third_metric"],
            mock_config
        )

    @patch('src.tools.metricflow.list_entities.run_mf_command')
    def test_list_entities_ignored_parameters(self, mock_run_command, mock_config):
        """Test that unexpected parameters are ignored."""
        # Mock command output
        mock_output = "entities"
        mock_run_command.return_value = (mock_output, None)

        # Run list entities with extra parameters
        result_json, stdout = list_entities(
            mock_config,
            metrics=["test"],
            unknown_param="ignored",
            another_param=123
        )

        # Verify only valid parameters were used
        mock_run_command.assert_called_once_with(
            ["list", "entities", "--metrics", "test"],
            mock_config
        )
