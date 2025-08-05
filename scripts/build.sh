#!/bin/bash
# Copyright (c) 2025 Shishir Bondre
# Licensed under the Creative Commons Attribution-NonCommercial 4.0 International License
# See LICENSE file for details

# Build Docker image for Multi-Repository Git MCP Server

set -e

IMAGE_NAME="git-mcp-server"
IMAGE_TAG="latest"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Building Multi-Repository Git MCP Server Docker Image ==="

# Check if Docker is installed and running
if ! command -v docker &>/dev/null; then
    echo "❌ Error: Docker is required but not installed"
    exit 1
fi
if ! docker info &>/dev/null; then
    echo "❌ Error: Docker is not running"
    exit 1
fi
echo "✅ Docker is available"

# Build the Docker image
echo "Building image: $IMAGE_NAME:$IMAGE_TAG"
docker build -t "$IMAGE_NAME:$IMAGE_TAG" "$SCRIPT_DIR/.."

echo "✅ Docker image '$IMAGE_NAME:$IMAGE_TAG' built successfully!"
echo "See docs/installation.md for deployment instructions."