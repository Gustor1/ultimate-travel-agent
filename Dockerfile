# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8001 \
    HOST=0.0.0.0 \
    TRAVEL_MCP_PORT=8001 \
    TRAVEL_MCP_HOST=0.0.0.0

# Set work directory
WORKDIR /app

# Create non-root user and group
RUN groupadd -g 1001 traveler && \
    useradd -u 1001 -g traveler -s /bin/bash -m traveler

# Install package build and runtime essentials
COPY pyproject.toml README.md /app/
COPY src/ /app/src/
COPY packages/ /app/packages/
COPY config/ /app/config/

# Install the application and mcp + web extras
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e ".[mcp,web]"

# Ensure correct permissions for the non-root traveler user
RUN chown -R traveler:traveler /app

# Switch to non-root user
USER traveler

# Healthcheck using standard library urllib (no curl dependency needed)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import os, urllib.request; port = os.environ.get('PORT', '8001'); urllib.request.urlopen(f'http://localhost:{port}/health')" || exit 1

# Expose HTTP port
EXPOSE 8001

# Entrypoint running Streamable HTTP MCP server
CMD ["python", "-m", "ultimate_travel_agent.cli", "mcp-http"]
