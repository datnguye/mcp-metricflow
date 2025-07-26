"""MetricFlow list metrics functionality."""

import json

from config.config import MfCliConfig
from tools.metricflow.base import run_mf_command


def list_metrics(config: MfCliConfig, **kwargs) -> tuple[str, str]:
    """List available metrics with their dimensions.

    Args:
        config: Configuration containing paths and settings
        **kwargs: Optional parameters including search, show_all_dimensions
    """
    args = ["list", "metrics"]

    # Add optional parameters
    if kwargs.get("search"):
        args.extend(["--search", kwargs["search"]])
    if kwargs.get("show_all_dimensions", False):
        args.append("--show-all-dimensions")

    stdout, stderr = run_mf_command(args, config)
    return json.dumps({"info": stdout, "error": stderr}), stdout
