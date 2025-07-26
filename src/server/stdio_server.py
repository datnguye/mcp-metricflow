"""STDIO server module for MetricFlow MCP server."""

import asyncio
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.stdio import stdio_server

from config.config import load_mf_config
from tools.cli_tools import register_mf_cli_tools
from utils.logger import logger


async def _register_tools(mcp_server: FastMCP, config: Any) -> None:
    """Register MCP tools based on configuration."""
    logger.info("Registering mf CLI tools")
    logger.info(f"Configuration: project_dir={config.project_dir}, mf_path={config.mf_path}, tmp_dir={config.tmp_dir}")
    register_mf_cli_tools(mcp_server, config)
    logger.info("✓ Successfully registered mf CLI tools")


async def run_stdio_server() -> None:
    """Run the MCP server in STDIO mode."""
    logger.info("Starting MCP server in STDIO mode")

    try:
        # Load configuration
        config = load_mf_config()
        logger.info("Loaded config: %s", config)

        # Initialize MCP server
        mcp_server = FastMCP(name="mf")

        # Register tools
        await _register_tools(mcp_server, config)

        # Run STDIO server
        async with stdio_server() as (read_stream, write_stream):
            logger.info("STDIO streams connected, starting MCP server communication")
            await mcp_server._mcp_server.run(
                read_stream, write_stream, mcp_server._mcp_server.create_initialization_options()
            )
            logger.info("STDIO connection closed")

    except Exception as e:
        logger.error("Failed to run STDIO server: %s", e)
        raise


def main() -> None:
    """Entry point for STDIO server."""
    logger.info("=" * 60)
    logger.info("Starting MetricFlow MCP Server (STDIO mode)")
    logger.info("=" * 60)

    asyncio.run(run_stdio_server())
