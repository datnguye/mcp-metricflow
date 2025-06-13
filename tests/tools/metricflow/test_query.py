"""Tests for the query module."""

import csv
import json
import os
import pytest
from pathlib import Path
from unittest.mock import patch, Mock, mock_open, MagicMock

from src.tools.metricflow.query import query
from src.config.config import MfCliConfig


class TestQuery:
    """Test cases for query function."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock MfCliConfig for testing."""
        return MfCliConfig(
            project_dir="/test/project",
            profiles_dir="/test/profiles",
            mf_path="/usr/bin/mf",
            tmp_dir="/tmp/metricflow"
        )

    @pytest.fixture
    def csv_data(self):
        """Sample CSV data for testing."""
        return """metric,dimension,value
revenue,US,1000
revenue,EU,800
orders,US,50
orders,EU,40"""

    @patch('src.tools.metricflow.query.run_mf_command')
    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('os.remove')
    @patch('builtins.open', new_callable=mock_open)
    @patch('csv.DictReader')
    def test_query_basic_metrics(self, mock_csv_reader, mock_file, mock_remove,
                                 mock_exists, mock_makedirs, mock_run_command, mock_config):
        """Test basic query with metrics."""
        # Mock CSV data
        mock_csv_reader.return_value = [
            {"metric": "revenue", "value": "1000"},
            {"metric": "revenue", "value": "800"}
        ]

        # Mock successful command
        mock_run_command.return_value = ("Query executed", None)
        mock_exists.return_value = True

        # Run query
        message, data = query("session1", ["revenue"], mock_config)

        # Verify command was called correctly
        expected_args = [
            "query", "--metrics", "revenue", "--limit", "100",
            "--csv", "/tmp/metricflow/mf_query_result_session1.csv"
        ]
        mock_run_command.assert_called_once_with(expected_args, mock_config)

        # Verify directory creation
        mock_makedirs.assert_called_once_with("/tmp/metricflow", exist_ok=True)

        # Verify file cleanup
        mock_remove.assert_called_once_with("/tmp/metricflow/mf_query_result_session1.csv")

        # Verify output
        message_dict = json.loads(message)
        assert message_dict["info"] == "Query executed"
        assert message_dict["error"] is None

        data_list = json.loads(data)
        assert len(data_list) == 2

    @patch('src.tools.metricflow.query.run_mf_command')
    @patch('os.makedirs')
    def test_query_with_saved_query(self, mock_makedirs, mock_run_command, mock_config):
        """Test query with saved query parameter."""
        # Mock command output
        mock_run_command.return_value = ("Saved query executed", None)

        # Run query with saved query
        message, data = query("session1", [], mock_config, saved_query="my_saved_query")

        # Verify command was called with saved query
        expected_args = [
            "query", "--saved-query", "my_saved_query", "--limit", "100",
            "--csv", "/tmp/metricflow/mf_query_result_session1.csv"
        ]
        mock_run_command.assert_called_once_with(expected_args, mock_config)

    def test_query_no_metrics_or_saved_query(self, mock_config):
        """Test query without metrics or saved query."""
        # Run query without metrics or saved query
        message, data = query("session1", [], mock_config)

        # Verify error is returned
        message_dict = json.loads(message)
        assert "Either metrics or saved_query must be specified" in message_dict["error"]
        assert data == "[]"

    @patch('src.tools.metricflow.query.run_mf_command')
    @patch('os.makedirs')
    def test_query_with_all_parameters(self, mock_makedirs, mock_run_command, mock_config):
        """Test query with all possible parameters."""
        # Mock command output
        mock_run_command.return_value = ("Complex query executed", None)

        # Run query with all parameters
        message, data = query(
            "session1",
            ["revenue", "orders"],
            mock_config,
            group_by=["region", "date"],
            start_time="2023-01-01",
            end_time="2023-12-31",
            where="region = 'US'",
            order=["revenue", "desc"],
            limit=50,
            explain=True,
            show_dataflow_plan=True,
            show_sql_descriptions=True
        )

        # Verify command was called with all parameters
        expected_args = [
            "query", "--metrics", "revenue,orders",
            "--group-by", "region,date",
            "--start-time", "2023-01-01",
            "--end-time", "2023-12-31",
            "--where", "region = 'US'",
            "--order", "revenue,desc",
            "--limit", "50",
            "--explain",
            "--show-dataflow-plan",
            "--show-sql-descriptions",
            "--csv", "/tmp/metricflow/mf_query_result_session1.csv"
        ]
        mock_run_command.assert_called_once_with(expected_args, mock_config)

    @patch('src.tools.metricflow.query.run_mf_command')
    @patch('os.makedirs')
    def test_query_boolean_flags_false(self, mock_makedirs, mock_run_command, mock_config):
        """Test query with boolean flags set to False."""
        # Mock command output
        mock_run_command.return_value = ("Query executed", None)

        # Run query with boolean flags set to False
        message, data = query(
            "session1",
            ["revenue"],
            mock_config,
            explain=False,
            show_dataflow_plan=False,
            show_sql_descriptions=False
        )

        # Verify boolean flags are not included
        expected_args = [
            "query", "--metrics", "revenue", "--limit", "100",
            "--csv", "/tmp/metricflow/mf_query_result_session1.csv"
        ]
        mock_run_command.assert_called_once_with(expected_args, mock_config)

    @patch('src.tools.metricflow.query.run_mf_command')
    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_query_with_error(self, mock_exists, mock_makedirs, mock_run_command, mock_config):
        """Test query with command error."""
        # Mock command error
        mock_run_command.return_value = ("", "Query failed")
        mock_exists.return_value = False

        # Run query
        message, data = query("session1", ["revenue"], mock_config)

        # Verify error handling
        message_dict = json.loads(message)
        assert message_dict["error"] == "Query failed"
        assert data == "[]"

    @patch('src.tools.metricflow.query.run_mf_command')
    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_query_csv_file_not_exists(self, mock_exists, mock_makedirs, mock_run_command, mock_config):
        """Test query when CSV file is not created."""
        # Mock successful command but no CSV file
        mock_run_command.return_value = ("Query executed", None)
        mock_exists.return_value = False

        # Run query
        message, data = query("session1", ["revenue"], mock_config)

        # Verify fallback to empty data
        assert data == "[]"

    @patch('src.tools.metricflow.query.run_mf_command')
    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('os.remove')
    @patch('builtins.open')
    def test_query_file_read_error(self, mock_open_file, mock_remove, mock_exists,
                                   mock_makedirs, mock_run_command, mock_config):
        """Test query when CSV file cannot be read."""
        # Mock successful command and file exists
        mock_run_command.return_value = ("Query executed", None)
        mock_exists.return_value = True
        mock_open_file.side_effect = IOError("Cannot read file")

        # Run query and expect exception
        with pytest.raises(IOError):
            query("session1", ["revenue"], mock_config)

    @patch('src.tools.metricflow.query.run_mf_command')
    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('os.remove')
    @patch('builtins.open', new_callable=mock_open)
    @patch('csv.DictReader')
    def test_query_csv_cleanup_on_success(self, mock_csv_reader, mock_file, mock_remove,
                                          mock_exists, mock_makedirs, mock_run_command, mock_config):
        """Test that CSV file is cleaned up after successful processing."""
        # Mock data
        mock_csv_reader.return_value = [{"col": "value"}]
        mock_run_command.return_value = ("Success", None)
        mock_exists.return_value = True

        # Run query
        query("session1", ["revenue"], mock_config)

        # Verify cleanup
        mock_remove.assert_called_once_with("/tmp/metricflow/mf_query_result_session1.csv")

    @patch('src.tools.metricflow.query.run_mf_command')
    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('os.remove')
    @patch('builtins.open', new_callable=mock_open)
    @patch('csv.DictReader')
    def test_query_csv_cleanup_on_exception(self, mock_csv_reader, mock_file, mock_remove,
                                           mock_exists, mock_makedirs, mock_run_command, mock_config):
        """Test that CSV file is cleaned up even when exception occurs."""
        # Mock data and exception
        mock_csv_reader.side_effect = Exception("CSV error")
        mock_run_command.return_value = ("Success", None)
        mock_exists.return_value = True

        # Run query and expect exception
        with pytest.raises(Exception):
            query("session1", ["revenue"], mock_config)

        # Verify cleanup still happened
        mock_remove.assert_called_once_with("/tmp/metricflow/mf_query_result_session1.csv")

    @patch('src.tools.metricflow.query.run_mf_command')
    @patch('os.makedirs')
    def test_query_limit_none(self, mock_makedirs, mock_run_command, mock_config):
        """Test query with limit set to None."""
        # Mock command output
        mock_run_command.return_value = ("Query executed", None)

        # Run query with limit=None
        message, data = query("session1", ["revenue"], mock_config, limit=None)

        # Verify limit parameter is not included
        args_called = mock_run_command.call_args[0][0]
        assert "--limit" not in args_called

    @patch('src.tools.metricflow.query.run_mf_command')
    @patch('os.makedirs')
    def test_query_empty_lists_handling(self, mock_makedirs, mock_run_command, mock_config):
        """Test query with empty group_by and order lists."""
        # Mock command output
        mock_run_command.return_value = ("Query executed", None)

        # Run query with empty lists
        message, data = query(
            "session1",
            ["revenue"],
            mock_config,
            group_by=[],
            order=[]
        )

        # Verify empty lists don't add parameters
        args_called = mock_run_command.call_args[0][0]
        assert "--group-by" not in args_called
        assert "--order" not in args_called
