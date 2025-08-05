#!/bin/bash
# Copyright (c) 2025 Shishir Bondre
# Licensed under the Creative Commons Attribution-NonCommercial 4.0 International License
# See LICENSE file for details

# Test Multi-Repository Git MCP Server functionality

set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 <base_repos_directory>"
    echo "Example: $0 /Users/john/Projects"
    exit 1
fi

BASE_REPOS_DIR="$(realpath "$1")"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTAINER_NAME="multi-git-mcp-server"

echo "=== Testing Multi-Repository Git MCP Server ==="
echo "Base repository directory: $BASE_REPOS_DIR"
echo ""

# Validate base directory
if [ ! -d "$BASE_REPOS_DIR" ]; then
    echo "❌ Error: $BASE_REPOS_DIR does not exist"
    exit 1
fi
echo "✅ Base repository directory validated"

# Check Docker
if ! command -v docker &>/dev/null; then
    echo "❌ Error: Docker is required but not installed"
    exit 1
fi
if ! docker info &>/dev/null; then
    echo "❌ Error: Docker is not running"
    exit 1
fi
echo "✅ Docker is available"

# Cleanup existing container
cleanup() {
    echo "Cleaning up container: $CONTAINER_NAME"
    docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
}
trap cleanup EXIT

# Create test sequence
create_test_sequence() {
    echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}'
    echo '{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}'
    sleep 0.5
    echo '{"jsonrpc":"2.0","id":2,"method":"resources/list","params":{}}'
    echo '{"jsonrpc":"2.0","id":3,"method":"resources/read","params":{"uri":"git://repositories"}}'
    echo '{"jsonrpc":"2.0","id":4,"method":"tools/list","params":{}}'
    echo '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"list_repositories","arguments":{}}}'
}

echo "Running MCP protocol test..."
(
    create_test_sequence | "$SCRIPT_DIR/run_docker_mcp.sh" "$BASE_REPOS_DIR" &
    SERVER_PID=$!
    # Wait up to 15 seconds
    for i in {1..30}; do
        if ! kill -0 $SERVER_PID 2>/dev/null; then
            break
        fi
        sleep 0.5
    done
    kill $SERVER_PID 2>/dev/null || true
    wait $SERVER_PID 2>/dev/null || true
) | while IFS= read -r line; do
    echo "$(date '+%H:%M:%S') | $line"
done

echo ""
echo "🎉 Test completed!"
echo ""
echo "If JSON responses are shown above, the server is working correctly."
echo "Expected responses:"
echo "  1. Initialize response with server info"
echo "  2. Resources list including git://repositories and git://current"
echo "  3. Repository discovery results"
echo "  4. Available tools list"
echo "  5. List of discovered repositories"
echo ""
echo "See docs/usage.md for how to use the server."