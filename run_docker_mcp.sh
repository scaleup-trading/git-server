#!/bin/bash

# Docker wrapper for Multi-Repo Git MCP Server with persistent state

set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 <base_repos_directory>" >&2
    echo "Example: $0 /Users/john/Projects" >&2
    exit 1
fi

BASE_REPOS_DIR="$(realpath "$1")"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_DIR="$SCRIPT_DIR/state"
CONTAINER_NAME="multi-git-mcp-server"
IMAGE_NAME="git-mcp-server"

# Validate base directory exists
if [ ! -d "$BASE_REPOS_DIR" ]; then
    echo "Error: $BASE_REPOS_DIR does not exist" >&2
    exit 1
fi

# Create state directory if it doesn't exist
mkdir -p "$STATE_DIR"

# Cleanup on exit
cleanup() {
    docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
}
trap cleanup EXIT

# Run container with persistent state and stdio
# Mount the entire base repos directory as read-only
exec docker run -i --rm \
    --name "$CONTAINER_NAME" \
    -v "$BASE_REPOS_DIR:/repos:ro" \
    -v "$STATE_DIR:/app/state" \
    "$IMAGE_NAME" /repos