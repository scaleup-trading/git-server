FROM python:3.11-slim

WORKDIR /app

# Install Git
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the MCP server script
COPY git_mcp_server.py .
COPY git_operations.py .
COPY file_manager.py .
COPY repository_manager.py .
COPY diff_processor.py .
COPY state_manager.py .
COPY workspace_manager.py .
RUN chmod +x *.py

# Create state directory for persistent storage
RUN mkdir -p /app/state

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Mount points
VOLUME ["/repos"]
VOLUME ["/app/state"]

# Entry point expects base repos directory as argument
ENTRYPOINT ["python3", "git_mcp_server.py"]
CMD ["/repos"]