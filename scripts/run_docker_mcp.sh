#!/bin/bash
# Copyright (c) 2025 Shishir Bondre
# Licensed under the Creative Commons Attribution-NonCommercial 4.0 International License
# See LICENSE file for details

# Docker wrapper for Multi-Repository Git MCP Server with persistent state

set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 <base_repos_directory>" >&2
    echo "Example: $0 /Users/john/Projects" >&2
    exit 1
fi

BASE_REPOS_DIR="$(realpath "$1")"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_DIR="$SCRIPT_DIR/../state"
CONTAINER_NAME="multi-git-mcp-server"
IMAGE_NAME="git-mcp-server:latest"

echo "=== Starting Multi-Repository Git MCP Server ==="

# Validate base directory
if [ ! -d "$BASE_REPOS_DIR" ]; then
    echo "❌ Error: $BASE_REPOS_DIR does not exist" >&2
    exit 1
fi
echo "✅ Base repository directory: $BASE_REPOS_DIR"

# Check if Docker is installed and running
if ! command -v docker &>/dev/null; then
    echo "❌ Error: Docker is required but not installed" >&2
    exit 1
fi
if ! docker info &>/dev/null; then
    echo "❌ Error: Docker is not running" >&2
    exit 1
fi
echo "✅ Docker is available"

# Create state directory
mkdir -p "$STATE_DIR"
echo "✅ State directory: $STATE_DIR"

# Cleanup existing container
cleanup() {
    echo "Cleaning up container: $CONTAINER_NAME"
    docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
}
trap cleanup EXIT

# Run the Docker container
echo "Starting container: $CONTAINER_NAME"
exec docker run -i --rm \
    --name "$CONTAINER_NAME" \
    -v "$BASE_REPOS_DIR:/repos:ro" \
    -v "$STATE_DIR:/app/state" \
    "$IMAGE_NAME" /repos