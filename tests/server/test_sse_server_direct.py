"""Direct tests for SSE server to improve coverage."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from contextlib import asynccontextmanager

from src.server.sse_server import app_lifespan, handle_sse


class TestSseServerDirect:
    """Direct tests for SSE server functionality."""

    @pytest.mark.asyncio
    async def test_app_lifespan_exception_in_startup(self):
        """Test app_lifespan when exception occurs during startup."""
        mock_app = Mock()
        mock_app.state = Mock()

        with patch('src.server.sse_server.load_mf_config') as mock_load_config:
            mock_load_config.side_effect = Exception("Config load error")

            with patch('src.server.sse_server.logger') as mock_logger:
                lifespan_ctx = app_lifespan(mock_app)

                with pytest.raises(Exception, match="Config load error"):
                    async with lifespan_ctx:
                        pass

                # Verify error was logged
                mock_logger.error.assert_called_with("Failed to start MCP server: %s", mock_load_config.side_effect)

    @pytest.mark.asyncio
    async def test_handle_sse_no_mcp_server_attribute(self):
        """Test handle_sse when mf_mcp attribute doesn't exist."""
        mock_request = Mock()
        mock_request.app.state = Mock(spec=[])  # Empty spec means no attributes

        with patch('src.server.sse_server.logger') as mock_logger:
            result = await handle_sse(mock_request, True)

            assert result is None
            mock_logger.error.assert_called_with("MCP server not initialized")

    @pytest.mark.asyncio
    async def test_handle_sse_successful_connection(self):
        """Test handle_sse with successful SSE connection."""
        # Mock request with proper app state
        mock_request = Mock()
        mock_mcp_server = Mock()
        mock_mcp_server._mcp_server = Mock()
        mock_mcp_server._mcp_server.run = AsyncMock()
        mock_mcp_server._mcp_server.create_initialization_options = Mock(return_value={})

        mock_request.app.state.mf_mcp = mock_mcp_server
        mock_request.scope = {"type": "http"}
        mock_request.receive = AsyncMock()
        mock_request._send = AsyncMock()

        # Create a proper async context manager for transport
        @asynccontextmanager
        async def mock_connect_sse(*args):
            mock_streams = (Mock(), Mock())
            yield mock_streams

        with patch('src.server.sse_server.transport') as mock_transport:
            mock_transport.connect_sse = mock_connect_sse

            with patch('src.server.sse_server.logger') as mock_logger:
                await handle_sse(mock_request, True)

                # Verify the MCP server run was called
                mock_mcp_server._mcp_server.run.assert_called_once()

                # Verify logging
                mock_logger.info.assert_any_call("New SSE connection established")
                mock_logger.info.assert_any_call("SSE streams connected, starting MCP server communication")
                mock_logger.info.assert_any_call("SSE connection closed")
