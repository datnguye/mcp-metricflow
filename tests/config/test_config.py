"""Tests for the config module."""

import os
import pytest
from pathlib import Path
from unittest.mock import patch

from src.config.config import MfCliConfig, load_mf_config


class TestMfCliConfig:
    """Test cases for MfCliConfig dataclass."""

    def test_mf_cli_config_creation(self):
        """Test creating MfCliConfig instance."""
        config = MfCliConfig(
            project_dir="/path/to/project",
            profiles_dir="/path/to/profiles",
            mf_path="/usr/bin/mf",
            tmp_dir="/tmp/metricflow"
        )

        assert config.project_dir == "/path/to/project"
        assert config.profiles_dir == "/path/to/profiles"
        assert config.mf_path == "/usr/bin/mf"
        assert config.tmp_dir == "/tmp/metricflow"

    def test_mf_cli_config_attributes(self):
        """Test MfCliConfig has all required attributes."""
        config = MfCliConfig(
            project_dir="test",
            profiles_dir="test",
            mf_path="test",
            tmp_dir="test"
        )

        assert hasattr(config, 'project_dir')
        assert hasattr(config, 'profiles_dir')
        assert hasattr(config, 'mf_path')
        assert hasattr(config, 'tmp_dir')


class TestLoadMfConfig:
    """Test cases for load_mf_config function."""

    @patch.dict(os.environ, clear=True)
    @patch('src.config.config.load_dotenv')
    def test_load_mf_config_with_all_env_vars(self, mock_load_dotenv):
        """Test loading config when all environment variables are set."""
        os.environ.update({
            'DBT_PROJECT_DIR': '/custom/project',
            'DBT_PROFILES_DIR': '/custom/profiles',
            'MF_PATH': '/custom/bin/mf',
            'MF_TMP_DIR': '/custom/tmp/metricflow'
        })

        config = load_mf_config()

        assert config.project_dir == '/custom/project'
        assert config.profiles_dir == '/custom/profiles'
        assert config.mf_path == '/custom/bin/mf'
        assert config.tmp_dir == '/custom/tmp/metricflow'
        mock_load_dotenv.assert_called_once()

    @patch.dict(os.environ, clear=True)
    @patch('src.config.config.load_dotenv')
    def test_load_mf_config_with_defaults(self, mock_load_dotenv):
        """Test loading config when only required environment variable is set."""
        os.environ['DBT_PROJECT_DIR'] = '/my/project'

        config = load_mf_config()

        assert config.project_dir == '/my/project'
        assert config.profiles_dir == os.path.expanduser("~/.dbt")
        assert config.mf_path == 'mf'
        assert config.tmp_dir == os.path.join(os.path.expanduser("~/.dbt"), "metricflow")
        mock_load_dotenv.assert_called_once()

    @patch.dict(os.environ, clear=True)
    @patch('src.config.config.load_dotenv')
    def test_load_mf_config_with_no_project_dir(self, mock_load_dotenv):
        """Test loading config when DBT_PROJECT_DIR is not set."""
        # Clear any existing DBT_PROJECT_DIR
        os.environ.pop('DBT_PROJECT_DIR', None)

        config = load_mf_config()

        assert config.project_dir is None
        assert config.profiles_dir == os.path.expanduser("~/.dbt")
        assert config.mf_path == 'mf'
        assert config.tmp_dir == os.path.join(os.path.expanduser("~/.dbt"), "metricflow")
        mock_load_dotenv.assert_called_once()

    @patch.dict(os.environ, clear=True)
    @patch('src.config.config.load_dotenv')
    def test_load_mf_config_with_partial_env_vars(self, mock_load_dotenv):
        """Test loading config with some environment variables set."""
        os.environ.update({
            'DBT_PROJECT_DIR': '/partial/project',
            'DBT_PROFILES_DIR': '/partial/profiles',
            # MF_PATH and MF_TMP_DIR not set, should use defaults
        })

        config = load_mf_config()

        assert config.project_dir == '/partial/project'
        assert config.profiles_dir == '/partial/profiles'
        assert config.mf_path == 'mf'
        assert config.tmp_dir == os.path.join(os.path.expanduser("~/.dbt"), "metricflow")
        mock_load_dotenv.assert_called_once()

    @patch.dict(os.environ, clear=True)
    @patch('src.config.config.load_dotenv')
    def test_load_mf_config_empty_env_vars(self, mock_load_dotenv):
        """Test loading config when environment variables are empty strings."""
        os.environ.update({
            'DBT_PROJECT_DIR': '',
            'DBT_PROFILES_DIR': '',
            'MF_PATH': '',
            'MF_TMP_DIR': ''
        })

        config = load_mf_config()

        # Empty strings should be preserved, not replaced with defaults
        assert config.project_dir == ''
        assert config.profiles_dir == ''
        assert config.mf_path == ''
        assert config.tmp_dir == ''
        mock_load_dotenv.assert_called_once()

    @patch.dict(os.environ, clear=True)
    @patch('src.config.config.load_dotenv')
    def test_load_dotenv_called(self, mock_load_dotenv):
        """Test that load_dotenv is called when loading config."""
        os.environ['DBT_PROJECT_DIR'] = '/test/project'

        load_mf_config()

        mock_load_dotenv.assert_called_once()
