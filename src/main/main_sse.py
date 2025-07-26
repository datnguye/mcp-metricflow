"""Main entry point for MetricFlow MCP server (SSE mode)."""

import os

import uvicorn

from server.sse_server import app
from utils.logger import configure_logging

# Configure logging
logger = configure_logging()


if __name__ == "__main__":
    # Run in SSE mode
    host = os.environ.get("MCP_HOST", "0.0.0.0")  # nosec B104
    port = int(os.environ.get("MCP_PORT", "8000"))

    logger.info("=" * 60)
    logger.info("Starting MetricFlow MCP Server (SSE mode)")
    logger.info("=" * 60)
    logger.info(f"Server will be available at http://{host}:{port}")

    uvicorn.run(app, host=host, port=port, log_level="info", access_log=True)
