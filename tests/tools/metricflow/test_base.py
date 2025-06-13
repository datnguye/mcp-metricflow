"""Tests for the metricflow base module."""

import os
import subprocess
import pytest
from unittest.mock import Mock, patch, MagicMock, call

from src.tools.metricflow.base import run_mf_command
from src.config.config import MfCliConfig


class TestRunMfCommand:
    """Test cases for run_mf_command function."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock MfCliConfig for testing."""
        return MfCliConfig(
            project_dir="/test/project",
            profiles_dir="/test/profiles",
            mf_path="/usr/bin/mf",
            tmp_dir="/tmp/metricflow"
        )

    @patch('subprocess.Popen')
    @patch('src.tools.metricflow.base.logger')
    def test_run_mf_command_success(self, mock_logger, mock_popen, mock_config):
        """Test successful command execution."""
        # Mock process
        mock_process = Mock()
        mock_process.communicate.return_value = ("Success output", None)
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Run command
        stdout, stderr = run_mf_command(["list", "metrics"], mock_config)

        # Verify results
        assert stdout == "Success output"
        assert stderr is None

        # Verify Popen was called correctly
        mock_popen.assert_called_once_with(
            args=["/usr/bin/mf", "list", "metrics"],
            cwd="/test/project",
            env=pytest.approx(dict(os.environ, DBT_PROFILES_DIR="/test/profiles")),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # Verify logging
        mock_logger.info.assert_any_call("Executing MetricFlow command:")
        mock_logger.info.assert_any_call("  Command: /usr/bin/mf list metrics")
        mock_logger.info.assert_any_call("✓ Command completed successfully (exit code: 0)")

    @patch('subprocess.Popen')
    @patch('src.tools.metricflow.base.logger')
    def test_run_mf_command_failure(self, mock_logger, mock_popen, mock_config):
        """Test command execution failure."""
        # Mock process
        mock_process = Mock()
        mock_process.communicate.return_value = ("Error output", "Error details")
        mock_process.returncode = 1
        mock_popen.return_value = mock_process

        # Run command
        stdout, stderr = run_mf_command(["invalid", "command"], mock_config)

        # Verify results
        assert stdout == "Error output"
        assert stderr == "Error details"

        # Verify error logging
        mock_logger.error.assert_any_call("✗ Command failed (exit code: 1)")
        mock_logger.error.assert_any_call("ERR: Error details | Error output")

    @patch('subprocess.Popen')
    @patch('src.tools.metricflow.base.logger')
    def test_run_mf_command_with_query_adds_quiet(self, mock_logger, mock_popen, mock_config):
        """Test that query commands get --quiet flag added."""
        # Mock process
        mock_process = Mock()
        mock_process.communicate.return_value = ("Query result", None)
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Run query command
        stdout, stderr = run_mf_command(["query", "--metrics", "revenue"], mock_config)

        # Verify --quiet was added after query
        mock_popen.assert_called_once_with(
            args=["/usr/bin/mf", "query", "--quiet", "--metrics", "revenue"],
            cwd="/test/project",
            env=pytest.approx(dict(os.environ, DBT_PROFILES_DIR="/test/profiles")),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

    @patch('subprocess.Popen')
    def test_run_mf_command_empty_command(self, mock_popen, mock_config):
        """Test handling of empty command list."""
        # Mock process
        mock_process = Mock()
        mock_process.communicate.return_value = ("", None)
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Run empty command
        stdout, stderr = run_mf_command([], mock_config)

        # Verify command was executed with just the mf path
        mock_popen.assert_called_once_with(
            args=["/usr/bin/mf"],
            cwd="/test/project",
            env=pytest.approx(dict(os.environ, DBT_PROFILES_DIR="/test/profiles")),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

    @patch('subprocess.Popen')
    def test_run_mf_command_query_only(self, mock_popen, mock_config):
        """Test query command with no additional arguments."""
        # Mock process
        mock_process = Mock()
        mock_process.communicate.return_value = ("", None)
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Run query command alone
        stdout, stderr = run_mf_command(["query"], mock_config)

        # Verify --quiet was added
        mock_popen.assert_called_once_with(
            args=["/usr/bin/mf", "query", "--quiet"],
            cwd="/test/project",
            env=pytest.approx(dict(os.environ, DBT_PROFILES_DIR="/test/profiles")),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

    @patch('subprocess.Popen')
    @patch('src.tools.metricflow.base.logger')
    def test_run_mf_command_non_verbose_command(self, mock_logger, mock_popen, mock_config):
        """Test that non-verbose commands don't get --quiet flag."""
        # Mock process
        mock_process = Mock()
        mock_process.communicate.return_value = ("List output", None)
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Run non-verbose command
        stdout, stderr = run_mf_command(["list", "dimensions"], mock_config)

        # Verify --quiet was NOT added
        mock_popen.assert_called_once_with(
            args=["/usr/bin/mf", "list", "dimensions"],
            cwd="/test/project",
            env=pytest.approx(dict(os.environ, DBT_PROFILES_DIR="/test/profiles")),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

    @patch('subprocess.Popen')
    @patch('os.environ.copy')
    def test_run_mf_command_environment_setup(self, mock_env_copy, mock_popen, mock_config):
        """Test that environment is set up correctly."""
        # Mock environment
        mock_env = {"EXISTING_VAR": "value"}
        mock_env_copy.return_value = mock_env.copy()

        # Mock process
        mock_process = Mock()
        mock_process.communicate.return_value = ("", None)
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Run command
        run_mf_command(["test"], mock_config)

        # Verify environment was copied and modified
        mock_env_copy.assert_called_once()
        expected_env = mock_env.copy()
        expected_env["DBT_PROFILES_DIR"] = "/test/profiles"

        mock_popen.assert_called_once_with(
            args=["/usr/bin/mf", "test"],
            cwd="/test/project",
            env=expected_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

    @patch('subprocess.Popen')
    @patch('src.tools.metricflow.base.logger')
    def test_run_mf_command_logging_details(self, mock_logger, mock_popen, mock_config):
        """Test detailed logging of command execution."""
        # Mock process
        mock_process = Mock()
        mock_process.communicate.return_value = ("", None)
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Run command
        run_mf_command(["health-checks"], mock_config)

        # Verify all logging calls
        expected_calls = [
            call("=" * 60),
            call("Executing MetricFlow command:"),
            call("  Command: /usr/bin/mf health-checks"),
            call("  Working Dir: /test/project"),
            call("  Profiles Dir: /test/profiles"),
            call("=" * 60),
            call("✓ Command completed successfully (exit code: 0)")
        ]

        for expected_call in expected_calls:
            assert expected_call in mock_logger.info.call_args_list

    @patch('subprocess.Popen')
    def test_run_mf_command_with_complex_args(self, mock_popen, mock_config):
        """Test command with complex arguments."""
        # Mock process
        mock_process = Mock()
        mock_process.communicate.return_value = ("", None)
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Run command with complex args
        complex_args = [
            "query",
            "--metrics", "revenue,orders",
            "--dimensions", "ds,region",
            "--where", "region = 'US'"
        ]
        run_mf_command(complex_args, mock_config)

        # Verify command was constructed correctly with --quiet inserted
        expected_args = [
            "/usr/bin/mf", "query", "--quiet",
            "--metrics", "revenue,orders",
            "--dimensions", "ds,region",
            "--where", "region = 'US'"
        ]
        mock_popen.assert_called_once_with(
            args=expected_args,
            cwd="/test/project",
            env=pytest.approx(dict(os.environ, DBT_PROFILES_DIR="/test/profiles")),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
