"""MetricFlow validate configs functionality."""

import json

from config.config import MfCliConfig
from tools.metricflow.base import run_mf_command


def validate_configs(config: MfCliConfig, **kwargs) -> tuple[str, str]:
    """Perform validations against the defined model configurations.

    Args:
        config: Configuration containing paths and settings
        **kwargs: Optional parameters including dw_timeout, skip_dw, show_all,
                 verbose_issues, semantic_validation_workers
    """
    args = ["validate-configs"]

    # Add optional parameters
    if kwargs.get("dw_timeout"):
        args.extend(["--dw-timeout", str(kwargs["dw_timeout"])])
    if kwargs.get("skip_dw", False):
        args.append("--skip-dw")
    if kwargs.get("show_all", False):
        args.append("--show-all")
    if kwargs.get("verbose_issues", False):
        args.append("--verbose-issues")
    if kwargs.get("semantic_validation_workers"):
        args.extend(["--semantic-validation-workers", str(kwargs["semantic_validation_workers"])])

    stdout, stderr = run_mf_command(args, config)
    return json.dumps({"info": stdout, "error": stderr}), stdout
