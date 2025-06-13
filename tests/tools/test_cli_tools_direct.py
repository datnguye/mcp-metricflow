"""Direct tests for CLI tools to improve coverage."""

import pytest
from unittest.mock import Mock, patch

from src.tools.cli_tools import register_mf_cli_tools
from src.config.config import MfCliConfig


class TestCliToolsDirect:
    """Direct tests for CLI tools functionality."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock MfCliConfig for testing."""
        return MfCliConfig(
            project_dir="/test/project",
            profiles_dir="/test/profiles",
            mf_path="/usr/bin/mf",
            tmp_dir="/tmp/metricflow"
        )

    @patch('src.tools.cli_tools.load_prompt')
    @patch('src.tools.cli_tools.query')
    @patch('src.tools.cli_tools.list_metrics')
    @patch('src.tools.cli_tools.list_dimensions')
    @patch('src.tools.cli_tools.list_entities')
    @patch('src.tools.cli_tools.list_dimension_values')
    @patch('src.tools.cli_tools.validate_configs')
    @patch('src.tools.cli_tools.health_checks')
    def test_tool_functions_called_directly(self, mock_health_checks, mock_validate_configs,
                                          mock_list_dimension_values, mock_list_entities,
                                          mock_list_dimensions, mock_list_metrics,
                                          mock_query, mock_load_prompt, mock_config):
        """Test that tool functions are called directly."""
        # Mock return values
        mock_load_prompt.return_value = "Test description"
        mock_query.return_value = ("query_result", "query_data")
        mock_list_metrics.return_value = ("metrics_result", "metrics_data")
        mock_list_dimensions.return_value = ("dimensions_result", "dimensions_data")
        mock_list_entities.return_value = ("entities_result", "entities_data")
        mock_list_dimension_values.return_value = ("values_result", "values_data")
        mock_validate_configs.return_value = ("validate_result", "validate_data")
        mock_health_checks.return_value = ("health_result", "health_data")

        # Create mock MCP that stores registered functions
        registered_functions = {}

        class MockMCP:
            def tool(self, description):
                def decorator(func):
                    registered_functions[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()

        # Register tools
        register_mf_cli_tools(mock_mcp, mock_config)

        # Test query tool
        query_tool = registered_functions['query_tool']
        result = query_tool(
            session_id="test",
            metrics=["revenue"],
            group_by=["region"],
            start_time="2023-01-01",
            end_time="2023-12-31",
            where="region = 'US'",
            order=["revenue"],
            limit=50,
            saved_query="test_query",
            explain=True,
            show_dataflow_plan=True,
            show_sql_descriptions=True
        )

        mock_query.assert_called_once_with(
            session_id="test",
            metrics=["revenue"],
            config=mock_config,
            group_by=["region"],
            start_time="2023-01-01",
            end_time="2023-12-31",
            where="region = 'US'",
            order=["revenue"],
            limit=50,
            saved_query="test_query",
            explain=True,
            show_dataflow_plan=True,
            show_sql_descriptions=True
        )
        assert result == ("query_result", "query_data")

        # Test list_metrics tool
        list_metrics_tool = registered_functions['list_metrics_tool']
        result = list_metrics_tool(search="revenue", show_all_dimensions=True)

        mock_list_metrics.assert_called_once_with(
            config=mock_config,
            search="revenue",
            show_all_dimensions=True
        )
        assert result == ("metrics_result", "metrics_data")

        # Test list_dimensions tool
        list_dimensions_tool = registered_functions['list_dimensions_tool']
        result = list_dimensions_tool(metrics=["revenue"])

        mock_list_dimensions.assert_called_once_with(
            config=mock_config,
            metrics=["revenue"]
        )
        assert result == ("dimensions_result", "dimensions_data")

        # Test list_entities tool
        list_entities_tool = registered_functions['list_entities_tool']
        result = list_entities_tool(metrics=["revenue"])

        mock_list_entities.assert_called_once_with(
            config=mock_config,
            metrics=["revenue"]
        )
        assert result == ("entities_result", "entities_data")

        # Test list_dimension_values tool
        list_dimension_values_tool = registered_functions['list_dimension_values_tool']
        result = list_dimension_values_tool(
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
        assert result == ("values_result", "values_data")

        # Test validate_configs tool
        validate_configs_tool = registered_functions['validate_configs_tool']
        result = validate_configs_tool(
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
        assert result == ("validate_result", "validate_data")

        # Test health_checks tool
        health_checks_tool = registered_functions['health_checks_tool']
        result = health_checks_tool()

        mock_health_checks.assert_called_once_with(config=mock_config)
        assert result == ("health_result", "health_data")
