#!/bin/bash

# Build Docker image for Git MCP Server

set -e

IMAGE_NAME="git-mcp-server"

echo "Building Git MCP Server Docker image..."
docker build -t "$IMAGE_NAME" .

echo "✅ Docker image '$IMAGE_NAME' built successfully!"