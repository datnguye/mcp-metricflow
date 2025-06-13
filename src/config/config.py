"""Configuration module for MetricFlow MCP server."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class MfCliConfig:
    """Configuration class for the MetricFlow CLI tool.

    Attributes:
        project_dir (str): Path to the dbt project directory.
        profiles_dir (str): Path to the dbt profiles directory.
        mf_path (str): Path to the mf executable.
        tmp_dir (str): Path to the temporary directory for query results.
    """

    project_dir: str
    profiles_dir: str
    mf_path: str
    tmp_dir: str


def load_mf_config() -> MfCliConfig:
    """Loads configuration for the MetricFlow CLI tool from environment variables.

    This function reads environment variables, specifically 'DBT_PROJECT_DIR', 'DBT_PROFILES_DIR',
    'MF_PATH', and 'MF_TMP_DIR', to construct and return an instance of MfCliConfig. It uses the
    `load_dotenv` function to load environment variables from a .env file if present.

    Returns:
        MfCliConfig: An instance of MfCliConfig populated with values from environment variables.
    """
    load_dotenv()

    project_dir = os.environ.get("DBT_PROJECT_DIR")
    profiles_dir = os.environ.get("DBT_PROFILES_DIR", os.path.expanduser("~/.dbt"))
    mf_path = os.environ.get("MF_PATH", "mf")
    tmp_dir = os.environ.get("MF_TMP_DIR", os.path.join(os.path.expanduser("~/.dbt"), "metricflow"))

    mf_cli_config = MfCliConfig(
        project_dir=project_dir,
        profiles_dir=profiles_dir,
        mf_path=mf_path,
        tmp_dir=tmp_dir,
    )

    return mf_cli_config
