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
        api_key (str | None): API key for SSE server authentication.
        require_auth (bool): Whether authentication is required for SSE endpoints.
    """

    project_dir: str
    profiles_dir: str
    mf_path: str
    tmp_dir: str
    api_key: str | None = None
    require_auth: bool = False


def load_mf_config() -> MfCliConfig:
    """Loads configuration for the MetricFlow CLI tool from environment variables.

    This function reads environment variables, specifically 'DBT_PROJECT_DIR', 'DBT_PROFILES_DIR',
    'MF_PATH', 'MF_TMP_DIR', 'MCP_API_KEY', and 'MCP_REQUIRE_AUTH', to construct and return an
    instance of MfCliConfig. It uses the `load_dotenv` function to load environment variables
    from a .env file if present.

    Returns:
        MfCliConfig: An instance of MfCliConfig populated with values from environment variables.
    """
    load_dotenv()

    project_dir = os.path.abspath(os.environ.get("DBT_PROJECT_DIR")) if os.environ.get("DBT_PROJECT_DIR") else None
    profiles_dir = os.path.abspath(os.environ.get("DBT_PROFILES_DIR", os.path.expanduser("~/.dbt")))
    mf_path = os.environ.get("MF_PATH", "mf")
    tmp_dir = os.environ.get("MF_TMP_DIR", os.path.join(os.path.expanduser("~/.dbt"), "metricflow"))

    # Authentication configuration
    api_key = os.environ.get("MCP_API_KEY")
    require_auth = os.environ.get("MCP_REQUIRE_AUTH", "false").lower() in ("true", "1", "yes", "on")

    mf_cli_config = MfCliConfig(
        project_dir=project_dir,
        profiles_dir=profiles_dir,
        mf_path=mf_path,
        tmp_dir=tmp_dir,
        api_key=api_key,
        require_auth=require_auth,
    )

    return mf_cli_config
