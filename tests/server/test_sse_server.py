"""Tests for the sse_server module."""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.server.sse_server import app_lifespan, _register_tools, health, handle_sse, app


class TestAppLifespan:
    """Test cases for app_lifespan function."""

    @pytest.mark.asyncio
    @patch('src.server.sse_server.load_mf_config')
    @patch('src.server.sse_server._register_tools')
    @patch('src.server.sse_server.FastMCP')
    @patch('src.server.sse_server.logger')
    async def test_app_lifespan_success(self, mock_logger, mock_fastmcp, mock_register_tools, mock_load_config):
        """Test successful app lifespan management."""
        # Mock configuration
        mock_config = Mock()
        mock_config.require_auth = False  # Disable auth for this test
        mock_config.api_key = None
        mock_load_config.return_value = mock_config

        # Mock FastMCP instance
        mock_mcp_server = Mock()
        mock_fastmcp.return_value = mock_mcp_server

        # Mock register_tools as async
        mock_register_tools.return_value = None

        # Create mock app
        mock_app = Mock()
        mock_app.state = Mock()

        # Test lifespan using async context manager
        async with app_lifespan(mock_app):
            # Verify initialization during startup
            mock_load_config.assert_called_once()
            mock_fastmcp.assert_called_once_with(name="mf")
            mock_register_tools.assert_called_once_with(mock_mcp_server, mock_config)
            assert mock_app.state.mf_mcp == mock_mcp_server

            # Verify logging
            mock_logger.info.assert_any_call("Starting MCP server")
            mock_logger.info.assert_any_call("Loaded config: %s", mock_config)
            mock_logger.info.assert_any_call("MCP server started successfully")

        # Verify shutdown logging
        mock_logger.info.assert_any_call("Shutting down MCP server")

    @pytest.mark.asyncio
    @patch('src.server.sse_server.load_mf_config')
    @patch('src.server.sse_server.logger')
    async def test_app_lifespan_config_error(self, mock_logger, mock_load_config):
        """Test app lifespan with configuration error."""
        # Mock configuration error
        mock_load_config.side_effect = Exception("Config error")

        # Create mock app
        mock_app = Mock()
        mock_app.state = Mock()

        # Test lifespan with error
        with pytest.raises(Exception, match="Config error"):
            async with app_lifespan(mock_app):
                pass

        # Verify error logging
        mock_logger.error.assert_called_with("Failed to start MCP server: %s", mock_load_config.side_effect)

    @pytest.mark.asyncio
    @patch('src.server.sse_server.load_mf_config')
    @patch('src.server.sse_server._register_tools')
    @patch('src.server.sse_server.FastMCP')
    @patch('src.server.sse_server.logger')
    async def test_app_lifespan_auth_warning(self, mock_logger, mock_fastmcp, mock_register_tools, mock_load_config):
        """Test app lifespan with authentication required but no API key configured."""
        # Mock configuration with authentication required but no API key
        mock_config = Mock()
        mock_config.api_key = None
        mock_config.require_auth = True  # Enable auth to trigger validation error
        mock_load_config.return_value = mock_config

        # Mock FastMCP
        mock_mcp_instance = Mock()
        mock_fastmcp.return_value = mock_mcp_instance

        # Mock register tools
        mock_register_tools.return_value = None

        # Create mock app
        mock_app = Mock()
        mock_app.state = Mock()

        # Test lifespan - should raise ValueError for invalid auth config
        with pytest.raises(ValueError, match="API key is required when authentication is enabled"):
            async with app_lifespan(mock_app):
                pass

    @pytest.mark.asyncio
    @patch('src.server.sse_server.load_mf_config')
    @patch('src.server.sse_server._register_tools')
    @patch('src.server.sse_server.FastMCP')
    @patch('src.server.sse_server.logger')
    async def test_app_lifespan_auth_enabled_with_key(self, mock_logger, mock_fastmcp, mock_register_tools, mock_load_config):
        """Test app lifespan with authentication enabled and API key configured."""
        # Mock configuration with authentication enabled and API key present
        mock_config = Mock()
        mock_config.api_key = "a" * 32  # Valid API key
        mock_config.require_auth = True
        mock_load_config.return_value = mock_config

        # Mock FastMCP
        mock_mcp_instance = Mock()
        mock_fastmcp.return_value = mock_mcp_instance

        # Mock register tools
        mock_register_tools.return_value = None

        # Create mock app
        mock_app = Mock()
        mock_app.state = Mock()

        # Test lifespan with valid auth config
        async with app_lifespan(mock_app):
            # Verify auth logging
            mock_logger.info.assert_any_call("API key authentication enabled")

    @pytest.mark.asyncio
    @patch('src.server.sse_server.load_mf_config')
    @patch('src.server.sse_server._register_tools')
    @patch('src.server.sse_server.FastMCP')
    @patch('src.server.sse_server.logger')
    @patch('src.server.sse_server.validate_auth_config')  # Mock validation to prevent early failure
    async def test_app_lifespan_auth_enabled_no_key_logging(self, mock_validate, mock_logger, mock_fastmcp, mock_register_tools, mock_load_config):
        """Test app lifespan authentication logging when auth is required but no API key configured."""
        # Mock configuration with authentication required but no API key
        mock_config = Mock()
        mock_config.api_key = None  # No API key
        mock_config.require_auth = True
        mock_load_config.return_value = mock_config

        # Mock validation to not raise error (we're testing logging, not validation)
        mock_validate.return_value = None

        # Mock FastMCP
        mock_mcp_instance = Mock()
        mock_fastmcp.return_value = mock_mcp_instance

        # Mock register tools
        mock_register_tools.return_value = None

        # Create mock app
        mock_app = Mock()
        mock_app.state = Mock()

        # Test lifespan - should log warning about missing API key
        async with app_lifespan(mock_app):
            # Verify warning logging for missing API key
            mock_logger.warning.assert_any_call("Authentication required but no API key configured")

    @pytest.mark.asyncio
    @patch('src.server.sse_server.load_mf_config')
    @patch('src.server.sse_server._register_tools')
    @patch('src.server.sse_server.FastMCP')
    @patch('src.server.sse_server.logger')
    async def test_app_lifespan_register_tools_error(self, mock_logger, mock_fastmcp, mock_register_tools, mock_load_config):
        """Test app lifespan with tool registration error."""
        # Mock configuration
        mock_config = Mock()
        mock_config.require_auth = False  # Disable auth for this test
        mock_config.api_key = None
        mock_load_config.return_value = mock_config

        # Mock FastMCP instance
        mock_mcp_server = Mock()
        mock_fastmcp.return_value = mock_mcp_server

        # Mock register_tools error
        mock_register_tools.side_effect = Exception("Registration error")

        # Create mock app
        mock_app = Mock()
        mock_app.state = Mock()

        # Test lifespan with error
        with pytest.raises(Exception, match="Registration error"):
            async with app_lifespan(mock_app):
                pass


class TestRegisterTools:
    """Test cases for _register_tools function."""

    @pytest.mark.asyncio
    @patch('src.server.sse_server.register_mf_cli_tools')
    @patch('src.server.sse_server.logger')
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


class TestHealthEndpoint:
    """Test cases for health endpoint."""

    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Test health check endpoint."""
        result = await health()

        assert result == {"status": "healthy", "message": "MCP server is running"}


class TestHandleSse:
    """Test cases for handle_sse function."""

    @pytest.mark.asyncio
    @patch('src.server.sse_server.transport')
    @patch('src.server.sse_server.logger')
    async def test_handle_sse_success(self, mock_logger, mock_transport):
        """Test successful SSE handling."""
        # Mock request and app state
        mock_request = Mock()
        mock_request.scope = {}
        mock_request.receive = AsyncMock()
        mock_request._send = AsyncMock()

        mock_app_state = Mock()
        mock_mcp_server = Mock()
        mock_app_state.mf_mcp = mock_mcp_server
        mock_request.app.state = mock_app_state

        # Mock MCP server internals
        mock_mcp_server._mcp_server = Mock()
        mock_mcp_server._mcp_server.run = AsyncMock()
        mock_mcp_server._mcp_server.create_initialization_options = Mock(return_value={})

        # Mock transport connection using contextlib.asynccontextmanager approach
        from contextlib import asynccontextmanager

        @asynccontextmanager
        async def mock_connect_sse(*args):
            mock_streams = (Mock(), Mock())
            yield mock_streams

        mock_transport.connect_sse = mock_connect_sse

        # Handle SSE
        await handle_sse(mock_request, True)

        # Verify MCP server run was called
        mock_mcp_server._mcp_server.run.assert_called_once()

        # Verify logging
        mock_logger.info.assert_any_call("New SSE connection established")
        mock_logger.info.assert_any_call("SSE streams connected, starting MCP server communication")
        mock_logger.info.assert_any_call("SSE connection closed")

    @pytest.mark.asyncio
    @patch('src.server.sse_server.logger')
    async def test_handle_sse_no_mcp_server(self, mock_logger):
        """Test SSE handling when MCP server is not initialized."""
        # Mock request without MCP server
        mock_request = Mock()
        mock_request.app.state = Mock(spec=[])  # Empty spec means no attributes

        result = await handle_sse(mock_request, True)

        assert result is None
        mock_logger.error.assert_called_with("MCP server not initialized")

    @pytest.mark.asyncio
    @patch('src.server.sse_server.transport')
    @patch('src.server.sse_server.logger')
    async def test_handle_sse_exception(self, mock_logger, mock_transport):
        """Test SSE handling with exception."""
        # Mock request and app state
        mock_request = Mock()
        mock_request.scope = {}
        mock_request.receive = AsyncMock()
        mock_request._send = AsyncMock()

        mock_app_state = Mock()
        mock_mcp_server = Mock()
        mock_app_state.mf_mcp = mock_mcp_server
        mock_request.app.state = mock_app_state

        # Mock transport connection with exception
        mock_transport.connect_sse.side_effect = Exception("Connection error")

        result = await handle_sse(mock_request, True)

        assert result is None
        mock_logger.error.assert_called_with("Error handling SSE connection: %s", mock_transport.connect_sse.side_effect)


class TestAppConfiguration:
    """Test cases for FastAPI app configuration."""

    def test_app_configuration(self):
        """Test FastAPI app is configured correctly."""
        assert app.title == "mf MCP SSE Server"
        assert app.description == "MCP server with mf tools exposed over SSE"
        assert hasattr(app, 'version')

    def test_health_endpoint_integration(self):
        """Test health endpoint through test client."""
        with TestClient(app) as client:
            # Mock the lifespan to avoid startup issues
            with patch('src.server.sse_server.app_lifespan'):
                response = client.get("/health")

                assert response.status_code == 200
                assert response.json() == {"status": "healthy", "message": "MCP server is running"}


class TestGlobalVariables:
    """Test cases for global variables."""

    def test_transport_initialization(self):
        """Test that transport is initialized correctly."""
        # Import module and check transport exists
        from src.server.sse_server import transport

        # Verify transport is not None (it was successfully created)
        assert transport is not None
