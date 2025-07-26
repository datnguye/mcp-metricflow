"""MetricFlow list entities functionality."""

import json

from config.config import MfCliConfig
from tools.metricflow.base import run_mf_command


def list_entities(config: MfCliConfig, **kwargs) -> tuple[str, str]:
    """List all unique entities.

    Args:
        config: Configuration containing paths and settings
        **kwargs: Optional parameters including metrics
    """
    args = ["list", "entities"]

    # Add optional parameters
    if kwargs.get("metrics"):
        args.extend(["--metrics", ",".join(kwargs["metrics"])])

    stdout, stderr = run_mf_command(args, config)
    return json.dumps({"info": stdout, "error": stderr}), stdout
