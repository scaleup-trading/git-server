# Use a slim Python 3.11 base image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install Git and dependencies in a single layer to reduce image size
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY scripts/run_docker_mcp.sh ./scripts/run_docker_mcp.sh

# Create state directory for persistent storage
RUN mkdir -p /app/state && \
    chmod -R 755 /app/src/*.py /app/scripts/*.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Mount points for repositories and state
VOLUME ["/repos", "/app/state"]

ENTRYPOINT ["python3", "src/git_mcp_server.py"]
CMD ["/repos"]
```