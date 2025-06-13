# mcp-metricflow

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](htmlcov/index.html)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Package manager: uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

A Model Context Protocol (MCP) server that provides MetricFlow CLI tools through both SSE (with optional API key authentication) and STDIO interfaces.

> [!WARNING]
> This repository is a learning project focused on MetricFlow integration with MCP. For production use cases, please refer to the official [dbt-mcp](https://github.com/dbt-labs/dbt-mcp) implementation by dbt Labs.

## Table of Contents

- [mcp-metricflow](#mcp-metricflow)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the MCP Server](#running-the-mcp-server)
    - [STDIO Mode (Claude Desktop)](#stdio-mode-claude-desktop)
      - [Claude Desktop Configuration](#claude-desktop-configuration)
    - [SSE Mode](#sse-mode)
  - [Available Tools](#available-tools)
  - [Project Structure](#project-structure)
  - [Development](#development)
    - [Code Quality](#code-quality)
  - [TODO](#todo)

## Overview

This project provides a Model Context Protocol (MCP) server that wraps MetricFlow CLI commands, making them accessible through both Server-Sent Events (SSE) and Standard Input/Output (STDIO) interfaces. It enables seamless integration with Claude Desktop and other MCP-compatible clients.

## Installation

```bash
# Clone the repository
git clone https://github.com/datnguye/mcp-metricflow.git
cd mcp-metricflow

# Install dependencies
uv sync

# Copy environment template
cp .env.template .env
```

## Configuration

Edit the `.env` file with your specific configuration:

```bash
# Required: Path to your dbt project
DBT_PROJECT_DIR=/path/to/your/dbt/project

# Optional: Other configurations
DBT_PROFILES_DIR=~/.dbt
MF_PATH=mf
MF_TMP_DIR=/tmp

# SSE server configuration (optional)
MCP_HOST=localhost
MCP_PORT=8000

# API key authentication for SSE mode (optional)
MCP_API_KEY=your-secret-api-key
MCP_REQUIRE_AUTH=false
```

## Running the MCP Server

### STDIO Mode (Claude Desktop)

For integration with Claude Desktop, use STDIO mode:

```bash
uv run python src/main_stdio.py
```

#### Claude Desktop Configuration

Add this to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "metricflow": {
      "command": "uv",
      "args": ["run", "python", "/path/to/mcp-metricflow/src/main_stdio.py"],
      "cwd": "/path/to/mcp-metricflow",
      "env": {
        "DBT_PROJECT_DIR": "/path/to/your/dbt/project",
        "DBT_PROFILES_DIR": "~/.dbt",
        "MF_PATH": "mf"
      }
    }
  }
}
```

### SSE Mode

For web-based integration or direct HTTP access:

```bash
# export DBT_PROFILES_DIR=~/.dbt
uv run python src/main_sse.py
```

The server will start on `http://localhost:8000` (or the host/port specified in your environment variables).

#### API Key Authentication

The SSE server supports optional API key authentication. To enable authentication:

1. Set the required environment variables:
   ```bash
   export MCP_API_KEY="your-secret-api-key"
   export MCP_REQUIRE_AUTH="true"
   ```

2. Access authenticated endpoints by including the API key in the Authorization header:
   ```bash
   # Health check (no authentication required)
   curl http://localhost:8000/health

   # SSE endpoint (requires authentication when enabled)
   curl -H "Authorization: Bearer your-secret-api-key" http://localhost:8000/sse
   ```

**Authentication Configuration:**
- `MCP_API_KEY`: The secret API key for authentication (required when `MCP_REQUIRE_AUTH=true`)
- `MCP_REQUIRE_AUTH`: Enable/disable authentication (`true`, `1`, `yes`, `on` to enable; default: `false`)

**Security Notes:**
- The `/health` endpoint is always accessible without authentication for monitoring purposes
- The `/sse` endpoint requires authentication when `MCP_REQUIRE_AUTH=true`
- API keys are case-sensitive and support special characters
- Store API keys securely and avoid committing them to version control

## Available Tools

The MCP server exposes the following MetricFlow CLI tools:

| Tool | Description | Required Parameters | Optional Parameters |
|------|-------------|-------------------|-------------------|
| `query` | Execute MetricFlow queries | `session_id`, `metrics` | `group_by`, `start_time`, `end_time`, `where`, `order`, `limit`, `saved_query`, `explain`, `show_dataflow_plan`, `show_sql_descriptions` |
| `list_metrics` | List available metrics | None | `search`, `show_all_dimensions` |
| `list_dimensions` | List available dimensions | None | `metrics` |
| `list_entities` | List available entities | None | `metrics` |
| `list_dimension_values` | List values for a dimension | `dimension`, `metrics` | `start_time`, `end_time` |
| `validate_configs` | Validate model configurations | None | `dw_timeout`, `skip_dw`, `show_all`, `verbose_issues`, `semantic_validation_workers` |
| `health_checks` | Perform system health checks | None | None |

Each tool includes comprehensive documentation accessible through the MCP interface.

## Project Structure

```
src/
├── config/
│   └── config.py              # Configuration management
├── server/
│   ├── auth.py                # API key authentication
│   ├── sse_server.py          # SSE server implementation
│   └── stdio_server.py        # STDIO server implementation
├── tools/
│   ├── prompts/mf_cli/        # Tool documentation (*.md files)
│   ├── metricflow/            # MetricFlow CLI wrappers
│   │   ├── base.py            # Shared command execution
│   │   ├── query.py           # Query functionality
│   │   ├── list_metrics.py    # List metrics
│   │   ├── list_dimensions.py # List dimensions
│   │   ├── list_entities.py   # List entities
│   │   ├── list_dimension_values.py # List dimension values
│   │   ├── validate_configs.py # Configuration validation
│   │   └── health_checks.py   # Health checks
│   └── cli_tools.py           # MCP tool registration
├── utils/
│   ├── logger.py              # Logging configuration
│   └── prompts.py             # Prompt loading utilities
├── main_sse.py                # SSE server entry point
└── main_stdio.py              # STDIO server entry point
```

## Development

### Code Quality

The project uses ruff for code formatting and linting:

```bash
# Format code
uv run ruff format

# Check code quality
uv run ruff check .
```

## TODO
- Test STDIO mode
