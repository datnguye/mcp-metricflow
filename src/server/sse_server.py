"""FastAPI server module for MetricFlow MCP server."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from importlib.metadata import version
from typing import Any

from fastapi import FastAPI, Request
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport

from config.config import load_mf_config
from server.auth import Authenticated, validate_auth_config
from tools.cli_tools import register_mf_cli_tools
from utils.logger import logger

# Global variables
transport = SseServerTransport("/messages/")


@asynccontextmanager
async def app_lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application lifecycle and MCP server initialization."""
    logger.info("Starting MCP server")

    try:
        # Load configuration
        config = load_mf_config()
        logger.info("Loaded config: %s", config)

        # Validate authentication configuration
        validate_auth_config(config)

        # Store config in app state for authentication
        app.state.config = config

        # Initialize MCP server and store in app state
        mcp_server = FastMCP(name="mf")
        app.state.mf_mcp = mcp_server

        # Register tools based on configuration
        await _register_tools(mcp_server, config)

        # Log authentication configuration
        if config.require_auth:
            if config.api_key:
                logger.info("API key authentication enabled")
            else:
                logger.warning("Authentication required but no API key configured")
        else:
            logger.info("API key authentication disabled")

        logger.info("MCP server started successfully")
        yield

    except Exception as e:
        logger.error("Failed to start MCP server: %s", e)
        raise
    finally:
        logger.info("Shutting down MCP server")


async def _register_tools(mcp_server: FastMCP, config: Any) -> None:
    """Register MCP tools based on configuration."""
    logger.info("Registering mf CLI tools")
    logger.info(f"Configuration: project_dir={config.project_dir}, mf_path={config.mf_path}, tmp_dir={config.tmp_dir}")
    register_mf_cli_tools(mcp_server, config)
    logger.info("✓ Successfully registered mf CLI tools")


# Initialize FastAPI app
app = FastAPI(
    title="mf MCP SSE Server",
    description="MCP server with mf tools exposed over SSE",
    version=version("mcp-metricflow"),
    lifespan=app_lifespan,
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "message": "MCP server is running"}


@app.get("/sse")
async def handle_sse(request: Request, _: Authenticated) -> None:
    """Handle SSE connections for MCP communication."""
    logger.info("New SSE connection established")

    mf_mcp = request.app.state.mf_mcp if hasattr(request.app.state, "mf_mcp") else None
    if not mf_mcp:
        logger.error("MCP server not initialized")
        return

    try:
        # Prepare bidirectional streams over SSE
        async with transport.connect_sse(request.scope, request.receive, request._send) as (in_stream, out_stream):
            logger.info("SSE streams connected, starting MCP server communication")
            # Run the MCP server
            await mf_mcp._mcp_server.run(in_stream, out_stream, mf_mcp._mcp_server.create_initialization_options())
            logger.info("SSE connection closed")
    except Exception as e:
        logger.error("Error handling SSE connection: %s", e)
        return


# Mount the SSE transport for POST messages
app.mount("/messages/", transport.handle_post_message)
