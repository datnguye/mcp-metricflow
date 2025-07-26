"""MetricFlow list dimensions functionality."""

import json

from config.config import MfCliConfig
from tools.metricflow.base import run_mf_command


def list_dimensions(config: MfCliConfig, **kwargs) -> tuple[str, str]:
    """List all unique dimensions.

    Args:
        config: Configuration containing paths and settings
        **kwargs: Optional parameters including metrics
    """
    args = ["list", "dimensions"]

    # Add optional parameters
    if kwargs.get("metrics"):
        args.extend(["--metrics", ",".join(kwargs["metrics"])])

    stdout, stderr = run_mf_command(args, config)
    return json.dumps({"info": stdout, "error": stderr}), stdout
