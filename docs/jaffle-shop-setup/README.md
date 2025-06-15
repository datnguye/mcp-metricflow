# Setting Up Jaffle Shop with MCP MetricFlow Server for Claude Desktop (STDIO)

This guide will walk you through setting up the `mcp-metricflow` server with the Jaffle Shop dbt project and integrating it with Claude Desktop using Docker in STDIO mode.

**Table of Contents**

- [Setting Up Jaffle Shop with MCP MetricFlow Server for Claude Desktop (STDIO)](#setting-up-jaffle-shop-with-mcp-metricflow-server-for-claude-desktop-stdio)
  - [Prerequisites](#prerequisites)
  - [Step 1: Set Up Jaffle Shop dbt Project](#step-1-set-up-jaffle-shop-dbt-project)
    - [1.1 Clone the Jaffle Shop Project](#11-clone-the-jaffle-shop-project)
    - [1.2 Set Up DuckDB (Recommended for Local Development)](#12-set-up-duckdb-recommended-for-local-development)
    - [1.3 Install and Run dbt](#13-install-and-run-dbt)
    - [1.4 Verify Semantic Layer Configuration](#14-verify-semantic-layer-configuration)
  - [Step 2: Set Up the MCP MetricFlow Server with Docker](#step-2-set-up-the-mcp-metricflow-server-with-docker)
    - [2.1 Copy Docker Files](#21-copy-docker-files)
    - [2.2 Build and Start the Container](#22-build-and-start-the-container)
    - [2.3 Test MetricFlow in the Container](#23-test-metricflow-in-the-container)
  - [Step 3: Configure Claude Desktop](#step-3-configure-claude-desktop)
    - [3.1 Locate Claude Desktop Configuration](#31-locate-claude-desktop-configuration)
    - [3.2 Add MCP Server Configuration](#32-add-mcp-server-configuration)
    - [3.3 Alternative: Using Direct Container Run (Advanced)](#33-alternative-using-direct-container-run-advanced)
    - [3.4 Restart Claude Desktop](#34-restart-claude-desktop)
  - [Step 4: Test the Integration](#step-4-test-the-integration)
    - [4.1 Basic MetricFlow Commands](#41-basic-metricflow-commands)
    - [4.2 Advanced Queries](#42-advanced-queries)
    - [4.3 Health Checks](#43-health-checks)
  - [Troubleshooting](#troubleshooting)
    - [Common Issues](#common-issues)
      - [1. Container Not Starting](#1-container-not-starting)
      - [2. dbt Connection Issues](#2-dbt-connection-issues)
      - [3. Claude Desktop Not Connecting](#3-claude-desktop-not-connecting)
      - [4. MetricFlow Commands Failing](#4-metricflow-commands-failing)
    - [Debug Mode](#debug-mode)
  - [Security Considerations](#security-considerations)
    - [1. Network Security](#1-network-security)
    - [2. File System Security](#2-file-system-security)
    - [3. Container Security](#3-container-security)
  - [Advanced Configuration](#advanced-configuration)
    - [1. Custom Semantic Models](#1-custom-semantic-models)
    - [2. Multiple Environment Support](#2-multiple-environment-support)
    - [3. Performance Optimization](#3-performance-optimization)
  - [Next Steps](#next-steps)

## Prerequisites

Before starting, ensure you have:

- **Docker Desktop** installed and running
  - [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
  - [Docker Installation Guide](https://docs.docker.com/get-docker/)
- **Claude Desktop** application installed
  - [Download Claude Desktop](https://claude.ai/download)
  - [Claude Desktop Documentation](https://docs.anthropic.com/en/docs/claude-code)
- **Git** for cloning repositories
  - [Download Git](https://git-scm.com/downloads)
  - [Git Installation Guide](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- **Basic understanding** of dbt and semantic layers
  - [dbt Documentation](https://docs.getdbt.com/)
  - [dbt Semantic Layer Guide](https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-semantic-layer)
  - [MetricFlow Documentation](https://docs.getdbt.com/docs/build/metricflow)

## Step 1: Set Up Jaffle Shop dbt Project

### 1.1 Clone the Jaffle Shop Project

```bash
# Clone the jaffle shop project with semantic layer support
git clone https://github.com/dbt-labs/jaffle-sl-template.git
cd jaffle-sl-template

# Or use the original jaffle shop if you prefer to add semantic layer yourself
# git clone https://github.com/dbt-labs/jaffle_shop.git
```

### 1.2 Set Up DuckDB (Recommended for Local Development)

Create a `profiles.yml` file in your home directory (`~/.dbt/profiles.yml`):

```yaml
jaffle_shop:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: jaffle_shop.duckdb
      extensions:
        - httpfs
        - parquet
```

### 1.3 Install and Run dbt

```bash
# Install dbt with DuckDB adapter
pip install dbt-duckdb

# Install dependencies
dbt deps

# Run the models
dbt run

# Test the models
dbt test
```

### 1.4 Verify Semantic Layer Configuration

Ensure your `dbt_project.yml` includes semantic layer configuration:

```yaml
# dbt_project.yml
name: 'jaffle_shop'
version: '1.0.0'

# ... other configurations ...

semantic-models:
  - name: orders
    model: ref('orders')
    dimensions:
      - name: order_date
        type: time
        type_params:
          time_granularity: day
      - name: customer_id
        type: categorical
    measures:
      - name: order_total
        agg: sum
        expr: amount
```

## Step 2: Set Up the MCP MetricFlow Server with Docker

### 2.1 Copy Docker Files

This directory contains the necessary Docker files:
- `Dockerfile` - Container configuration for the MCP server
- `docker-compose.yml` - Service orchestration configuration

Copy these files to your jaffle shop project directory:

```bash
# Copy Docker files to your project
cp Dockerfile /path/to/your/jaffle-sl-template/
cp docker-compose.yml /path/to/your/jaffle-sl-template/
cd /path/to/your/jaffle-sl-template/

# Copy the environment template from the main project
cp /path/to/mcp-metricflow/.env.template .env

# Edit the .env file with your specific configuration
# For basic STDIO setup, the defaults should work fine
```

### 2.2 Configure Environment Variables

Edit the `.env` file to match your setup. For the jaffle shop example with DuckDB:

```bash
# Required: Path to your dbt project
DBT_PROJECT_DIR=/dbt-project

# dbt profiles directory (default should work in container)
DBT_PROFILES_DIR=/root/.dbt

# MetricFlow executable path (default should work)
MF_PATH=mf

# Temporary directory for query results
MF_TMP_DIR=/tmp

# Authentication (not needed for STDIO mode)
MCP_REQUIRE_AUTH=false
MCP_API_KEY=
```

**Note**: For STDIO mode with Claude Desktop, you typically don't need authentication. The SSE-related configurations are only needed if you plan to run the server in web mode.

For a complete list of all available configuration options, see the main [`.env.template`](../../.env.template) file in the project root.

### 2.3 Build and Start the Container

```bash
# Build the Docker image
docker-compose build mcp-metricflow

# Start the STDIO container
docker-compose up -d mcp-metricflow

# Verify the container is running
docker-compose ps
```

### 2.4 Test MetricFlow in the Container

```bash
# Test MetricFlow commands in the container
docker-compose exec mcp-metricflow uv run mf --help
docker-compose exec mcp-metricflow uv run mf list metrics
```

## Step 3: Configure Claude Desktop

### 3.1 Locate Claude Desktop Configuration

Find your Claude Desktop configuration file:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### 3.2 Add MCP Server Configuration

Add the following configuration to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "metricflow": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "mcp-metricflow-stdio",
        "uv",
        "run",
        "python",
        "src/main_stdio.py"
      ],
      "env": {
        "DBT_PROJECT_DIR": "/dbt-project",
        "DBT_PROFILES_DIR": "/root/.dbt",
        "MF_PATH": "mf",
        "MF_TMP_DIR": "/tmp"
      }
    }
  }
}
```

### 3.3 Alternative: Using Direct Container Run (Advanced)

For better performance, you can use a direct container run:

```json
{
  "mcpServers": {
    "metricflow": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--name", "mcp-metricflow-claude",
        "-v", "/Users/$(whoami)/jaffle-sl-template:/dbt-project:ro",
        "-v", "/Users/$(whoami)/.dbt:/root/.dbt:ro",
        "jaffle-sl-template_mcp-metricflow",
        "uv", "run", "python", "src/main_stdio.py"
      ],
      "env": {
        "DBT_PROJECT_DIR": "/dbt-project",
        "DBT_PROFILES_DIR": "/root/.dbt"
      }
    }
  }
}
```

### 3.4 Restart Claude Desktop

After updating the configuration:

1. **Quit Claude Desktop** completely
2. **Restart Claude Desktop**
3. **Check for MCP connection** in the status bar

## Step 4: Test the Integration

### 4.1 Basic MetricFlow Commands

Open Claude Desktop and try these prompts:

```
Can you list all available metrics in my dbt project?
```

```
Show me the dimensions available for the orders metric.
```

```
Query the total revenue by month for the last 6 months.
```

### 4.2 Advanced Queries

```
What are the top 5 customers by total order value?
```

```
Show me the order trends by day of week for the current quarter.
```

```
Validate my semantic layer configurations and show any issues.
```

### 4.3 Health Checks

```
Run health checks on my MetricFlow setup.
```

## Troubleshooting

### Common Issues

#### 1. Container Not Starting

```bash
# Check container logs
docker-compose logs mcp-metricflow

# Check if dbt project is accessible
docker-compose exec mcp-metricflow ls -la /dbt-project
```

#### 2. dbt Connection Issues

```bash
# Test dbt connection in container
docker-compose exec mcp-metricflow dbt debug --project-dir /dbt-project --profiles-dir /root/.dbt
```

#### 3. Claude Desktop Not Connecting

1. Check Claude Desktop logs (if available)
2. Verify container is running: `docker ps`
3. Test STDIO manually:
   ```bash
   echo '{"method": "tools/list"}' | docker exec -i mcp-metricflow-stdio uv run python src/main_stdio.py
   ```

#### 4. MetricFlow Commands Failing

```bash
# Verify MetricFlow installation
docker-compose exec mcp-metricflow uv run mf --version

# Check if semantic models are detected
docker-compose exec mcp-metricflow uv run mf list metrics --project-dir /dbt-project
```

### Debug Mode

Enable debug logging by adding to your Docker environment:

```yaml
environment:
  - LOG_LEVEL=DEBUG
```

## Security Considerations

### 1. Network Security

- Keep the STDIO container isolated
- Use Docker networks for internal communication when needed

### 2. File System Security

- Mount dbt projects as read-only when possible
- Use specific volume mounts rather than broad filesystem access

### 3. Container Security

- Regularly update the base Docker image
- Scan images for vulnerabilities
- Use minimal user privileges within containers

## Advanced Configuration

### 1. Custom Semantic Models

Create advanced semantic models in your dbt project:

```yaml
# models/semantic_models/orders_semantic.yml
semantic_models:
  - name: orders_advanced
    model: ref('orders')
    dimensions:
      - name: order_date
        type: time
        type_params:
          time_granularity: day
      - name: customer_tier
        type: categorical
        expr:
          case
            when total_orders > 10 then 'VIP'
            when total_orders > 5 then 'Regular'
            else 'New'
          end
    measures:
      - name: revenue
        agg: sum
        expr: amount
      - name: order_count
        agg: count
        expr: order_id
      - name: avg_order_value
        agg: average
        expr: amount
```

### 2. Multiple Environment Support

Create different Docker compose configurations for different environments:

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  mcp-metricflow:
    extends:
      file: docker-compose.yml
      service: mcp-metricflow
    environment:
      - DBT_TARGET=prod
```

### 3. Performance Optimization

```yaml
# Optimize container resources
services:
  mcp-metricflow:
    # ... other config
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
    restart: unless-stopped
```

---

## Next Steps

Once you have the basic setup working:

1. **Explore Advanced Queries**: Try complex MetricFlow queries with multiple dimensions
2. **Add Custom Metrics**: Define business-specific metrics in your semantic models
3. **Set Up Monitoring**: Add logging and monitoring for production use

For more information, refer to:
- [MetricFlow Documentation](https://docs.getdbt.com/docs/build/metricflow)
- [dbt Semantic Layer](https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-semantic-layer)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
