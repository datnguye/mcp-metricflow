FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone the mcp-metricflow repository
RUN git clone https://github.com/datnguye/mcp-metricflow.git .

# Install uv
RUN pip install uv

# Install dependencies
RUN uv sync --all-extras

# Copy the dbt project
COPY . /dbt-project

# Set environment variables
ENV DBT_PROJECT_DIR=/dbt-project
ENV DBT_PROFILES_DIR=/root/.dbt
ENV MF_PATH=mf
ENV MF_TMP_DIR=/tmp

# Create .dbt directory and copy profiles
RUN mkdir -p /root/.dbt
COPY profiles.yml /root/.dbt/profiles.yml

# Default command for STDIO mode
CMD ["uv", "run", "python", "src/main_stdio.py"]
