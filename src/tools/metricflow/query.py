"""MetricFlow query functionality."""

import csv
import json
import os

from config.config import MfCliConfig
from tools.metricflow.base import run_mf_command


def query(session_id: str, metrics: list[str], config: MfCliConfig, **kwargs) -> tuple[str, str]:
    """Execute a MetricFlow query and return results.

    Args:
        session_id: Unique identifier for the query session
        metrics: List of metrics to query
        config: Configuration containing paths and settings
        **kwargs: Optional parameters including group_by, start_time, end_time, where,
                 order, limit, saved_query, explain, show_dataflow_plan, show_sql_descriptions
    """
    args = ["query"]
    saved_query = kwargs.get("saved_query")

    # Build command arguments
    if saved_query:
        args.extend(["--saved-query", saved_query])
    elif metrics:
        args.extend(["--metrics", ",".join(metrics)])
    else:
        return json.dumps({"error": "Either metrics or saved_query must be specified"}), "[]"

    # Add optional parameters using mapping
    group_by = kwargs.get("group_by")
    order = kwargs.get("order")
    limit = kwargs.get("limit", 100)

    param_map = {
        "--group-by": ",".join(group_by) if group_by else None,
        "--start-time": kwargs.get("start_time"),
        "--end-time": kwargs.get("end_time"),
        "--where": kwargs.get("where"),
        "--order": ",".join(order) if order else None,
        "--limit": str(limit) if limit is not None else None,
    }

    for flag, value in param_map.items():
        if value is not None:
            args.extend([flag, value])

    # Add boolean flags
    boolean_flags = [
        ("--explain", kwargs.get("explain", False)),
        ("--show-dataflow-plan", kwargs.get("show_dataflow_plan", False)),
        ("--show-sql-descriptions", kwargs.get("show_sql_descriptions", False)),
    ]
    args.extend(flag for flag, enabled in boolean_flags if enabled)

    # Execute command and handle CSV
    os.makedirs(config.tmp_dir, exist_ok=True)
    csv_file = f"{config.tmp_dir}/mf_query_result_{session_id}.csv"
    args.extend(["--csv", csv_file])

    stdout, stderr = run_mf_command(args, config)
    message = json.dumps({"info": stdout, "error": stderr})

    if stderr or not os.path.exists(csv_file):
        return message, "[]"

    try:
        with open(csv_file) as f:
            data = json.dumps(list(csv.DictReader(f)))
    finally:
        if os.path.exists(csv_file):
            os.remove(csv_file)

    return message, data
