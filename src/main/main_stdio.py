"""Main entry point for MetricFlow MCP server (STDIO mode)."""

from src.server.stdio_server import main as stdio_main
from src.utils.logger import configure_logging

# Configure logging
logger = configure_logging()


if __name__ == "__main__":
    # Run in STDIO mode
    stdio_main()
