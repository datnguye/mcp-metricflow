"""MetricFlow health checks functionality."""

import json

from config.config import MfCliConfig
from tools.metricflow.base import run_mf_command


def health_checks(config: MfCliConfig) -> tuple[str, str]:
    """Perform health checks against the data warehouse.

    Args:
        config: Configuration containing paths and settings
    """
    args = ["health-checks"]

    stdout, stderr = run_mf_command(args, config)
    return json.dumps({"info": stdout, "error": stderr}), stdout
