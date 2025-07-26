"""MetricFlow CLI tools module."""

from mcp.server.fastmcp import FastMCP

from config.config import MfCliConfig
from tools.metricflow.health_checks import health_checks
from tools.metricflow.list_dimension_values import list_dimension_values
from tools.metricflow.list_dimensions import list_dimensions
from tools.metricflow.list_entities import list_entities
from tools.metricflow.list_metrics import list_metrics
from tools.metricflow.query import query
from tools.metricflow.validate_configs import validate_configs
from utils.prompts import load_prompt


def register_mf_cli_tools(mf_mcp: FastMCP, config: MfCliConfig) -> None:
    """Registers MetricFlow CLI tools as callable functions within the provided FastMCP instance.

    This function defines and registers CLI tool commands, such as 'query', for use within the FastMCP
    framework. It wraps command execution logic to ensure certain commands (e.g., 'query') are run with
    reduced verbosity by adding the '--quiet' flag, minimizing output for improved efficiency and context
    window usage. The registered tools leverage the provided MfCliConfig for configuration details such as
    the MetricFlow binary path and project directory.

    Args:
        mf_mcp (FastMCP): The FastMCP instance to which CLI tools will be registered.
        config (MfCliConfig): Configuration object containing paths and settings for MetricFlow CLI usage.

    Returns:
        None
    """

    @mf_mcp.tool(description=load_prompt("mf_cli/query.md"))
    def query_tool(
        session_id: str,
        metrics: list[str],
        group_by: list[str] | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        where: str | None = None,
        order: list[str] | None = None,
        limit: int | None = 100,
        saved_query: str | None = None,
        explain: bool = False,
        show_dataflow_plan: bool = False,
        show_sql_descriptions: bool = False,
    ) -> tuple[str, str]:
        """MCP tool wrapper for the query function."""
        return query(
            session_id=session_id,
            metrics=metrics,
            config=config,
            **{
                "group_by": group_by,
                "start_time": start_time,
                "end_time": end_time,
                "where": where,
                "order": order,
                "limit": limit,
                "saved_query": saved_query,
                "explain": explain,
                "show_dataflow_plan": show_dataflow_plan,
                "show_sql_descriptions": show_sql_descriptions,
            },
        )

    @mf_mcp.tool(description=load_prompt("mf_cli/list_metrics.md"))
    def list_metrics_tool(
        search: str | None = None,
        show_all_dimensions: bool = False,
    ) -> tuple[str, str]:
        """MCP tool wrapper for the list_metrics function."""
        return list_metrics(
            config=config,
            **{
                "search": search,
                "show_all_dimensions": show_all_dimensions,
            },
        )

    @mf_mcp.tool(description=load_prompt("mf_cli/list_dimensions.md"))
    def list_dimensions_tool(
        metrics: list[str] | None = None,
    ) -> tuple[str, str]:
        """MCP tool wrapper for the list_dimensions function."""
        return list_dimensions(
            config=config,
            **{
                "metrics": metrics,
            },
        )

    @mf_mcp.tool(description=load_prompt("mf_cli/list_entities.md"))
    def list_entities_tool(
        metrics: list[str] | None = None,
    ) -> tuple[str, str]:
        """MCP tool wrapper for the list_entities function."""
        return list_entities(
            config=config,
            **{
                "metrics": metrics,
            },
        )

    @mf_mcp.tool(description=load_prompt("mf_cli/list_dimension_values.md"))
    def list_dimension_values_tool(
        dimension: str,
        metrics: list[str],
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> tuple[str, str]:
        """MCP tool wrapper for the list_dimension_values function."""
        return list_dimension_values(
            config=config,
            dimension=dimension,
            metrics=metrics,
            **{
                "start_time": start_time,
                "end_time": end_time,
            },
        )

    @mf_mcp.tool(description=load_prompt("mf_cli/validate_configs.md"))
    def validate_configs_tool(
        dw_timeout: int | None = None,
        skip_dw: bool = False,
        show_all: bool = False,
        verbose_issues: bool = False,
        semantic_validation_workers: int | None = None,
    ) -> tuple[str, str]:
        """MCP tool wrapper for the validate_configs function."""
        return validate_configs(
            config=config,
            **{
                "dw_timeout": dw_timeout,
                "skip_dw": skip_dw,
                "show_all": show_all,
                "verbose_issues": verbose_issues,
                "semantic_validation_workers": semantic_validation_workers,
            },
        )

    @mf_mcp.tool(description=load_prompt("mf_cli/health_checks.md"))
    def health_checks_tool() -> tuple[str, str]:
        """MCP tool wrapper for the health_checks function."""
        return health_checks(config=config)
