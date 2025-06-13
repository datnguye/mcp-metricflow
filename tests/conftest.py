"""Shared test fixtures and configuration."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables."""
    def _mock_env(**kwargs):
        for key, value in kwargs.items():
            monkeypatch.setenv(key, value)
    return _mock_env


@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run for CLI command testing."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(
            returncode=0,
            stdout='{"success": true}',
            stderr=''
        )
        yield mock_run


@pytest.fixture
def mock_mcp_server():
    """Mock MCP server for testing."""
    server = AsyncMock()
    server.request_context = AsyncMock()
    server.list_tools = AsyncMock(return_value=[])
    server.list_prompts = AsyncMock(return_value=[])
    return server
