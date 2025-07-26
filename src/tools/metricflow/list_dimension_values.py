"""MetricFlow list dimension values functionality."""

import json

from config.config import MfCliConfig
from tools.metricflow.base import run_mf_command


def list_dimension_values(config: MfCliConfig, dimension: str, metrics: list[str], **kwargs) -> tuple[str, str]:
    """List dimension values for given metrics.

    Args:
        config: Configuration containing paths and settings
        dimension: Dimension to query values from
        metrics: Metrics associated with the dimension
        **kwargs: Optional parameters including start_time, end_time
    """
    args = ["list", "dimension-values", "--dimension", dimension, "--metrics", ",".join(metrics)]

    # Add optional time constraints
    if kwargs.get("start_time"):
        args.extend(["--start-time", kwargs["start_time"]])
    if kwargs.get("end_time"):
        args.extend(["--end-time", kwargs["end_time"]])

    stdout, stderr = run_mf_command(args, config)
    return json.dumps({"info": stdout, "error": stderr}), stdout
