"""Tests for the stdio_server module."""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from src.server.stdio_server import _register_tools, run_stdio_server, main


class TestRegisterTools:
    """Test cases for _register_tools function."""

    @pytest.mark.asyncio
    @patch('src.server.stdio_server.register_mf_cli_tools')
    @patch('src.server.stdio_server.logger')
    async def test_register_tools_success(self, mock_logger, mock_register):
        """Test successful tool registration."""
        # Mock MCP server and config
        mock_mcp_server = Mock()
        mock_config = Mock()
        mock_config.project_dir = "/test/project"
        mock_config.mf_path = "/usr/bin/mf"
        mock_config.tmp_dir = "/tmp/test"

        # Register tools
        await _register_tools(mock_mcp_server, mock_config)

        # Verify registration
        mock_register.assert_called_once_with(mock_mcp_server, mock_config)

        # Verify logging
        mock_logger.info.assert_any_call("Registering mf CLI tools")
        mock_logger.info.assert_any_call(
            "Configuration: project_dir=/test/project, mf_path=/usr/bin/mf, tmp_dir=/tmp/test"
        )
        mock_logger.info.assert_any_call("✓ Successfully registered mf CLI tools")


class TestRunStdioServer:
    """Test cases for run_stdio_server function."""

    @pytest.mark.asyncio
    @patch('src.server.stdio_server.stdio_server')
    @patch('src.server.stdio_server._register_tools')
    @patch('src.server.stdio_server.FastMCP')
    @patch('src.server.stdio_server.load_mf_config')
    @patch('src.server.stdio_server.logger')
    async def test_run_stdio_server_success(self, mock_logger, mock_load_config,
                                           mock_fastmcp, mock_register_tools, mock_stdio_server):
        """Test successful STDIO server run."""
        # Mock configuration
        mock_config = Mock()
        mock_load_config.return_value = mock_config

        # Mock FastMCP instance
        mock_mcp_server = Mock()
        mock_mcp_server._mcp_server = Mock()
        mock_mcp_server._mcp_server.run = AsyncMock()
        mock_mcp_server._mcp_server.create_initialization_options = Mock(return_value={})
        mock_fastmcp.return_value = mock_mcp_server

        # Mock register_tools as async
        mock_register_tools.return_value = None

        # Mock stdio_server context manager
        mock_streams = (Mock(), Mock())
        mock_stdio_server.return_value.__aenter__ = AsyncMock(return_value=mock_streams)
        mock_stdio_server.return_value.__aexit__ = AsyncMock(return_value=None)

        # Run STDIO server
        await run_stdio_server()

        # Verify initialization
        mock_load_config.assert_called_once()
        mock_fastmcp.assert_called_once_with(name="mf")
        mock_register_tools.assert_called_once_with(mock_mcp_server, mock_config)

        # Verify MCP server run
        mock_mcp_server._mcp_server.run.assert_called_once_with(
            mock_streams[0], mock_streams[1], {}
        )

        # Verify logging
        mock_logger.info.assert_any_call("Starting MCP server in STDIO mode")
        mock_logger.info.assert_any_call("Loaded config: %s", mock_config)
        mock_logger.info.assert_any_call("STDIO streams connected, starting MCP server communication")
        mock_logger.info.assert_any_call("STDIO connection closed")

    @pytest.mark.asyncio
    @patch('src.server.stdio_server.load_mf_config')
    @patch('src.server.stdio_server.logger')
    async def test_run_stdio_server_config_error(self, mock_logger, mock_load_config):
        """Test STDIO server run with configuration error."""
        # Mock configuration error
        mock_load_config.side_effect = Exception("Config error")

        # Run STDIO server and expect exception
        with pytest.raises(Exception, match="Config error"):
            await run_stdio_server()

        # Verify error logging
        mock_logger.error.assert_called_with("Failed to run STDIO server: %s", mock_load_config.side_effect)

    @pytest.mark.asyncio
    @patch('src.server.stdio_server.stdio_server')
    @patch('src.server.stdio_server._register_tools')
    @patch('src.server.stdio_server.FastMCP')
    @patch('src.server.stdio_server.load_mf_config')
    @patch('src.server.stdio_server.logger')
    async def test_run_stdio_server_register_tools_error(self, mock_logger, mock_load_config,
                                                        mock_fastmcp, mock_register_tools, mock_stdio_server):
        """Test STDIO server run with tool registration error."""
        # Mock configuration
        mock_config = Mock()
        mock_load_config.return_value = mock_config

        # Mock FastMCP instance
        mock_mcp_server = Mock()
        mock_fastmcp.return_value = mock_mcp_server

        # Mock register_tools error
        mock_register_tools.side_effect = Exception("Registration error")

        # Run STDIO server and expect exception
        with pytest.raises(Exception, match="Registration error"):
            await run_stdio_server()

        # Verify error logging
        mock_logger.error.assert_called_with("Failed to run STDIO server: %s", mock_register_tools.side_effect)

    @pytest.mark.asyncio
    @patch('src.server.stdio_server.stdio_server')
    @patch('src.server.stdio_server._register_tools')
    @patch('src.server.stdio_server.FastMCP')
    @patch('src.server.stdio_server.load_mf_config')
    @patch('src.server.stdio_server.logger')
    async def test_run_stdio_server_mcp_run_error(self, mock_logger, mock_load_config,
                                                 mock_fastmcp, mock_register_tools, mock_stdio_server):
        """Test STDIO server run with MCP server run error."""
        # Mock configuration
        mock_config = Mock()
        mock_load_config.return_value = mock_config

        # Mock FastMCP instance
        mock_mcp_server = Mock()
        mock_mcp_server._mcp_server = Mock()
        mock_mcp_server._mcp_server.run = AsyncMock(side_effect=Exception("MCP run error"))
        mock_mcp_server._mcp_server.create_initialization_options = Mock(return_value={})
        mock_fastmcp.return_value = mock_mcp_server

        # Mock register_tools as async
        mock_register_tools.return_value = None

        # Mock stdio_server context manager
        mock_streams = (Mock(), Mock())
        mock_stdio_server.return_value.__aenter__ = AsyncMock(return_value=mock_streams)
        mock_stdio_server.return_value.__aexit__ = AsyncMock(return_value=None)

        # Run STDIO server and expect exception
        with pytest.raises(Exception, match="MCP run error"):
            await run_stdio_server()

    @pytest.mark.asyncio
    @patch('src.server.stdio_server.stdio_server')
    @patch('src.server.stdio_server._register_tools')
    @patch('src.server.stdio_server.FastMCP')
    @patch('src.server.stdio_server.load_mf_config')
    @patch('src.server.stdio_server.logger')
    async def test_run_stdio_server_stdio_connection_error(self, mock_logger, mock_load_config,
                                                          mock_fastmcp, mock_register_tools, mock_stdio_server):
        """Test STDIO server run with STDIO connection error."""
        # Mock configuration
        mock_config = Mock()
        mock_load_config.return_value = mock_config

        # Mock FastMCP instance
        mock_mcp_server = Mock()
        mock_fastmcp.return_value = mock_mcp_server

        # Mock register_tools as async
        mock_register_tools.return_value = None

        # Mock stdio_server context manager with error
        mock_stdio_server.side_effect = Exception("STDIO connection error")

        # Run STDIO server and expect exception
        with pytest.raises(Exception, match="STDIO connection error"):
            await run_stdio_server()


class TestMain:
    """Test cases for main function."""

    @patch('src.server.stdio_server.asyncio.run')
    @patch('src.server.stdio_server.logger')
    def test_main_success(self, mock_logger, mock_asyncio_run):
        """Test successful main function execution."""
        # Mock asyncio.run
        mock_asyncio_run.return_value = None

        # Run main
        main()

        # Verify asyncio.run was called with run_stdio_server
        mock_asyncio_run.assert_called_once()
        # Get the function that was passed to asyncio.run
        called_function = mock_asyncio_run.call_args[0][0]

        # Verify logging
        mock_logger.info.assert_any_call("=" * 60)
        mock_logger.info.assert_any_call("Starting MetricFlow MCP Server (STDIO mode)")
        mock_logger.info.assert_any_call("=" * 60)

    @patch('src.server.stdio_server.asyncio.run')
    @patch('src.server.stdio_server.logger')
    def test_main_with_asyncio_error(self, mock_logger, mock_asyncio_run):
        """Test main function with asyncio error."""
        # Mock asyncio.run error
        mock_asyncio_run.side_effect = Exception("Asyncio error")

        # Run main and expect exception
        with pytest.raises(Exception, match="Asyncio error"):
            main()

        # Verify asyncio.run was called
        mock_asyncio_run.assert_called_once()

    @patch('src.server.stdio_server.run_stdio_server')
    @patch('src.server.stdio_server.logger')
    def test_main_calls_run_stdio_server(self, mock_logger, mock_run_stdio_server):
        """Test that main function ultimately calls run_stdio_server."""
        # Mock run_stdio_server as async function
        mock_run_stdio_server.return_value = None

        # Import and patch asyncio.run
        with patch('asyncio.run') as mock_asyncio_run:
            mock_asyncio_run.return_value = None

            # Run main
            main()

            # Verify asyncio.run was called
            mock_asyncio_run.assert_called_once()

    def test_main_logging_format(self):
        """Test that main function logs with correct format."""
        with patch('src.server.stdio_server.asyncio.run') as mock_asyncio_run:
            with patch('src.server.stdio_server.logger') as mock_logger:
                mock_asyncio_run.return_value = None

                main()

                # Check that the logging calls include the banner format
                log_calls = mock_logger.info.call_args_list

                # Should have 3 calls: banner start, title, banner end
                assert len(log_calls) == 3
                assert log_calls[0][0][0] == "=" * 60
                assert "Starting MetricFlow MCP Server (STDIO mode)" in log_calls[1][0][0]
                assert log_calls[2][0][0] == "=" * 60
