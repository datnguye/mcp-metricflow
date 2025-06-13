"""Logging configuration for MetricFlow MCP server."""

import logging

# Global logger instance
logger = logging.getLogger("mcp-metricflow")


def configure_logging() -> logging.Logger:
    """Configure and return the logger for the application.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
    return logger
