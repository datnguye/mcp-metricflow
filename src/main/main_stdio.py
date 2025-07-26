"""Main entry point for MetricFlow MCP server (STDIO mode)."""

from server.stdio_server import main as stdio_main
from utils.logger import configure_logging

# Configure logging
logger = configure_logging()


def main() -> None:
    """Run the MetricFlow MCP server in STDIO mode."""
    stdio_main()


if __name__ == "__main__":
    # Run in STDIO mode
    main()
