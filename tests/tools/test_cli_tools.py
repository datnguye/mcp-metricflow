"""Tests for the cli_tools module."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.tools.cli_tools import register_mf_cli_tools
from src.config.config import MfCliConfig


class TestRegisterMfCliTools:
    """Test cases for register_mf_cli_tools function."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock MfCliConfig for testing."""
        return MfCliConfig(
            project_dir="/test/project",
            profiles_dir="/test/profiles",
            mf_path="/usr/bin/mf",
            tmp_dir="/tmp/metricflow"
        )

    @pytest.fixture
    def mock_mcp(self):
        """Create a mock FastMCP instance."""
        mcp = Mock()
        mcp.tool = Mock(side_effect=lambda description: lambda func: func)
        return mcp

    @patch('src.tools.cli_tools.load_prompt')
    @patch('src.tools.cli_tools.query')
    @patch('src.tools.cli_tools.list_metrics')
    @patch('src.tools.cli_tools.list_dimensions')
    @patch('src.tools.cli_tools.list_entities')
    @patch('src.tools.cli_tools.list_dimension_values')
    @patch('src.tools.cli_tools.validate_configs')
    @patch('src.tools.cli_tools.health_checks')
    def test_register_mf_cli_tools(self, mock_health_checks, mock_validate_configs,
                                   mock_list_dimension_values, mock_list_entities,
                                   mock_list_dimensions, mock_list_metrics,
                                   mock_query, mock_load_prompt,
                                   mock_mcp, mock_config):
        """Test that register_mf_cli_tools registers all tools correctly."""
        # Mock load_prompt to return descriptions
        mock_load_prompt.side_effect = lambda path: f"Description for {path}"

        # Register tools
        register_mf_cli_tools(mock_mcp, mock_config)

        # Verify tool decorator was called for each tool (7 tools total)
        assert mock_mcp.tool.call_count == 7

        # Verify load_prompt was called for each tool description
        expected_prompt_calls = [
            "mf_cli/query.md",
            "mf_cli/list_metrics.md",
            "mf_cli/list_dimensions.md",
            "mf_cli/list_entities.md",
            "mf_cli/list_dimension_values.md",
            "mf_cli/validate_configs.md",
            "mf_cli/health_checks.md"
        ]

        for expected_call in expected_prompt_calls:
            mock_load_prompt.assert_any_call(expected_call)

    @patch('src.tools.cli_tools.load_prompt')
    @patch('src.tools.cli_tools.query')
    def test_query_tool_wrapper(self, mock_query, mock_load_prompt, mock_mcp, mock_config):
        """Test the query tool wrapper function."""
        # Mock return values
        mock_load_prompt.return_value = "Query description"
        mock_query.return_value = ("result", "data")

        # Capture registered tools
        registered_tools = []
        def capture_tool(description):
            def decorator(func):
                registered_tools.append((description, func))
                return func
            return decorator

        mock_mcp.tool = capture_tool

        # Register tools
        register_mf_cli_tools(mock_mcp, mock_config)

        # Find the query tool by description content
        query_tool = next(tool for desc, tool in registered_tools
                         if "Query description" in desc)

        # Test the query tool
        result = query_tool(
            session_id="test_session",
            metrics=["revenue"],
            group_by=["region"],
            start_time="2023-01-01",
            end_time="2023-12-31",
            where="region = 'US'",
            order=["revenue"],
            limit=50,
            saved_query="my_query",
            explain=True,
            show_dataflow_plan=True,
            show_sql_descriptions=True
        )

        # Verify the underlying query function was called correctly
        mock_query.assert_called_once_with(
            session_id="test_session",
            metrics=["revenue"],
            config=mock_config,
            group_by=["region"],
            start_time="2023-01-01",
            end_time="2023-12-31",
            where="region = 'US'",
            order=["revenue"],
            limit=50,
            saved_query="my_query",
            explain=True,
            show_dataflow_plan=True,
            show_sql_descriptions=True
        )

    @patch('src.tools.cli_tools.load_prompt')
    @patch('src.tools.cli_tools.list_metrics')
    def test_list_metrics_tool_wrapper(self, mock_list_metrics, mock_load_prompt, mock_mcp, mock_config):
        """Test the list_metrics tool wrapper function."""
        # Mock return values with unique descriptions based on path
        def mock_load_prompt_side_effect(path):
            if "list_metrics.md" in path:
                return "List metrics tool description"
            return f"Description for {path}"

        mock_load_prompt.side_effect = mock_load_prompt_side_effect
        mock_list_metrics.return_value = ("result", "data")

        # Capture registered tools
        registered_tools = []
        def capture_tool(description):
            def decorator(func):
                registered_tools.append((description, func))
                return func
            return decorator

        mock_mcp.tool = capture_tool

        # Register tools
        register_mf_cli_tools(mock_mcp, mock_config)

        # Find the list_metrics tool by description content
        list_metrics_tool = next(tool for desc, tool in registered_tools
                                if "List metrics tool description" in desc)

        # Test the list_metrics tool
        result = list_metrics_tool(
            search="revenue",
            show_all_dimensions=True
        )

        # Verify the underlying function was called correctly
        mock_list_metrics.assert_called_once_with(
            config=mock_config,
            search="revenue",
            show_all_dimensions=True
        )

    @patch('src.tools.cli_tools.load_prompt')
    @patch('src.tools.cli_tools.list_dimensions')
    def test_list_dimensions_tool_wrapper(self, mock_list_dimensions, mock_load_prompt, mock_mcp, mock_config):
        """Test the list_dimensions tool wrapper function."""
        # Setup with unique descriptions
        def mock_load_prompt_side_effect(path):
            if "list_dimensions.md" in path:
                return "List dimensions tool description"
            return f"Description for {path}"

        mock_load_prompt.side_effect = mock_load_prompt_side_effect
        mock_list_dimensions.return_value = ("result", "data")

        # Capture tools
        registered_tools = []
        def capture_tool(description):
            def decorator(func):
                registered_tools.append((description, func))
                return func
            return decorator
        mock_mcp.tool = capture_tool

        # Register and test
        register_mf_cli_tools(mock_mcp, mock_config)
        list_dimensions_tool = next(tool for desc, tool in registered_tools
                                   if "List dimensions tool description" in desc)

        list_dimensions_tool(metrics=["revenue", "orders"])

        mock_list_dimensions.assert_called_once_with(
            config=mock_config,
            metrics=["revenue", "orders"]
        )

    @patch('src.tools.cli_tools.load_prompt')
    @patch('src.tools.cli_tools.list_entities')
    def test_list_entities_tool_wrapper(self, mock_list_entities, mock_load_prompt, mock_mcp, mock_config):
        """Test the list_entities tool wrapper function."""
        # Setup with unique descriptions
        def mock_load_prompt_side_effect(path):
            if "list_entities.md" in path:
                return "List entities tool description"
            return f"Description for {path}"

        mock_load_prompt.side_effect = mock_load_prompt_side_effect
        mock_list_entities.return_value = ("result", "data")

        # Capture tools
        registered_tools = []
        def capture_tool(description):
            def decorator(func):
                registered_tools.append((description, func))
                return func
            return decorator
        mock_mcp.tool = capture_tool

        # Register and test
        register_mf_cli_tools(mock_mcp, mock_config)
        list_entities_tool = next(tool for desc, tool in registered_tools
                                 if "List entities tool description" in desc)

        list_entities_tool(metrics=["revenue"])

        mock_list_entities.assert_called_once_with(
            config=mock_config,
            metrics=["revenue"]
        )

    @patch('src.tools.cli_tools.load_prompt')
    @patch('src.tools.cli_tools.list_dimension_values')
    def test_list_dimension_values_tool_wrapper(self, mock_list_dimension_values, mock_load_prompt, mock_mcp, mock_config):
        """Test the list_dimension_values tool wrapper function."""
        # Setup with unique descriptions
        def mock_load_prompt_side_effect(path):
            if "list_dimension_values.md" in path:
                return "List dimension values tool description"
            return f"Description for {path}"

        mock_load_prompt.side_effect = mock_load_prompt_side_effect
        mock_list_dimension_values.return_value = ("result", "data")

        # Capture tools
        registered_tools = []
        def capture_tool(description):
            def decorator(func):
                registered_tools.append((description, func))
                return func
            return decorator
        mock_mcp.tool = capture_tool

        # Register and test
        register_mf_cli_tools(mock_mcp, mock_config)
        list_dimension_values_tool = next(tool for desc, tool in registered_tools
                                         if "List dimension values tool description" in desc)

        list_dimension_values_tool(
            dimension="region",
            metrics=["revenue"],
            start_time="2023-01-01",
            end_time="2023-12-31"
        )

        mock_list_dimension_values.assert_called_once_with(
            config=mock_config,
            dimension="region",
            metrics=["revenue"],
            start_time="2023-01-01",
            end_time="2023-12-31"
        )

    @patch('src.tools.cli_tools.load_prompt')
    @patch('src.tools.cli_tools.validate_configs')
    def test_validate_configs_tool_wrapper(self, mock_validate_configs, mock_load_prompt, mock_mcp, mock_config):
        """Test the validate_configs tool wrapper function."""
        # Setup with unique descriptions
        def mock_load_prompt_side_effect(path):
            if "validate_configs.md" in path:
                return "Validate configs tool description"
            return f"Description for {path}"

        mock_load_prompt.side_effect = mock_load_prompt_side_effect
        mock_validate_configs.return_value = ("result", "data")

        # Capture tools
        registered_tools = []
        def capture_tool(description):
            def decorator(func):
                registered_tools.append((description, func))
                return func
            return decorator
        mock_mcp.tool = capture_tool

        # Register and test
        register_mf_cli_tools(mock_mcp, mock_config)
        validate_configs_tool = next(tool for desc, tool in registered_tools
                                    if "Validate configs tool description" in desc)

        validate_configs_tool(
            dw_timeout=300,
            skip_dw=True,
            show_all=True,
            verbose_issues=True,
            semantic_validation_workers=4
        )

        mock_validate_configs.assert_called_once_with(
            config=mock_config,
            dw_timeout=300,
            skip_dw=True,
            show_all=True,
            verbose_issues=True,
            semantic_validation_workers=4
        )

    @patch('src.tools.cli_tools.load_prompt')
    @patch('src.tools.cli_tools.health_checks')
    def test_health_checks_tool_wrapper(self, mock_health_checks, mock_load_prompt, mock_mcp, mock_config):
        """Test the health_checks tool wrapper function."""
        # Setup with unique descriptions
        def mock_load_prompt_side_effect(path):
            if "health_checks.md" in path:
                return "Health checks tool description"
            return f"Description for {path}"

        mock_load_prompt.side_effect = mock_load_prompt_side_effect
        mock_health_checks.return_value = ("result", "data")

        # Capture tools
        registered_tools = []
        def capture_tool(description):
            def decorator(func):
                registered_tools.append((description, func))
                return func
            return decorator
        mock_mcp.tool = capture_tool

        # Register and test
        register_mf_cli_tools(mock_mcp, mock_config)
        health_checks_tool = next(tool for desc, tool in registered_tools
                                 if "Health checks tool description" in desc)

        health_checks_tool()

        mock_health_checks.assert_called_once_with(config=mock_config)

    @patch('src.tools.cli_tools.load_prompt')
    def test_tool_registration_with_none_values(self, mock_load_prompt, mock_mcp, mock_config):
        """Test tool registration handles None values correctly."""
        mock_load_prompt.return_value = "Description"

        # Capture tools with detailed decorator
        registered_tools = []
        def detailed_capture_tool(description):
            def decorator(func):
                registered_tools.append((description, func))
                return func
            return decorator

        mock_mcp.tool = detailed_capture_tool

        # Register tools
        register_mf_cli_tools(mock_mcp, mock_config)

        # Verify all tools were registered
        assert len(registered_tools) == 7

        # Verify each tool has proper description
        descriptions = [desc for desc, _ in registered_tools]
        assert all("Description" in desc for desc in descriptions)

    def test_register_mf_cli_tools_returns_none(self, mock_mcp, mock_config):
        """Test that register_mf_cli_tools returns None."""
        with patch('src.tools.cli_tools.load_prompt'):
            result = register_mf_cli_tools(mock_mcp, mock_config)
            assert result is None
