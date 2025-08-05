#!/bin/bash

# Test Multi-Repo MCP server functionality

if [ $# -ne 1 ]; then
    echo "Usage: $0 <base_repos_directory>"
    echo "Example: $0 /Users/john/Projects"
    exit 1
fi

BASE_REPOS_DIR="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Testing Multi-Repo MCP Server ==="
echo "Base repos directory: $BASE_REPOS_DIR"
echo ""

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

# macOS compatible timeout using background process
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

    # Kill if still running
    kill $SERVER_PID 2>/dev/null || true
    wait $SERVER_PID 2>/dev/null || true
) | while IFS= read -r line; do
    echo "$(date '+%H:%M:%S') | $line"
done

echo ""
echo "Test completed!"
echo ""
echo "If you see JSON responses above, the Multi-Repo MCP server is working!"
echo ""
echo "Expected responses:"
echo "  1. Initialize response with server info"
echo "  2. Resources list with git://repositories and git://current"
echo "  3. Repository discovery results"
echo "  4. Available tools list"
echo "  5. List of discovered repositories"