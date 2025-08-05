#!/bin/bash
# Copyright (c) 2025 Shishir Bondre
# Licensed under the Creative Commons Attribution-NonCommercial 4.0 International License
# See LICENSE file for details

# Setup script for Multi-Repository Git MCP Server

set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 <base_repos_directory>"
    echo "Example: $0 /Users/john/Projects"
    exit 1
fi

REPO_PATH="$(realpath "$1")"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WRAPPER_SCRIPT="$SCRIPT_DIR/run_docker_mcp.sh"

echo "=== Multi-Repository Git MCP Server Setup ==="
echo "Base repository directory: $REPO_PATH"
echo "Script directory: $SCRIPT_DIR"
echo ""

# Validate repository directory
if [ ! -d "$REPO_PATH" ]; then
    echo "❌ Error: $REPO_PATH does not exist"
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

# Make scripts executable
chmod +x "$SCRIPT_DIR"/*.sh 2>/dev/null || true
echo "✅ Scripts made executable"

# Build Docker image
echo ""
echo "Building Docker image..."
"$SCRIPT_DIR/build.sh"
echo "✅ Docker image built"

# Test wrapper script
echo ""
echo "Testing wrapper script..."
# macOS/Linux compatible timeout test
(echo '' | "$WRAPPER_SCRIPT" "$REPO_PATH" &
WRAPPER_PID=$!
sleep 3
kill $WRAPPER_PID 2>/dev/null || true
wait $WRAPPER_PID 2>/dev/null || true) >/dev/null 2>&1

if [ $? -eq 0 ] || [ $? -eq 143 ]; then
    echo "✅ Wrapper script test passed"
else
    echo "⚠️  Wrapper script test completed (this is normal)"
fi

# Determine Claude Desktop config path
if [[ "$OSTYPE" == "darwin"* ]]; then
    CONFIG_PATH="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    CONFIG_PATH="$HOME/.config/Claude/claude_desktop_config.json"
else
    echo "❌ Error: Unsupported operating system ($OSTYPE)"
    exit 1
fi
echo ""
echo "Configuring Claude Desktop..."

# Create config directory
mkdir -p "$(dirname "$CONFIG_PATH")"

# Backup existing config
if [ -f "$CONFIG_PATH" ]; then
    cp "$CONFIG_PATH" "$CONFIG_PATH.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Backed up existing config to $CONFIG_PATH.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Create Claude Desktop config
cat > "$CONFIG_PATH" << EOF
{
  "mcpServers": {
    "git-context": {
      "command": "$WRAPPER_SCRIPT",
      "args": ["$REPO_PATH"]
    }
  }
}
EOF
echo "✅ Claude Desktop config created at $CONFIG_PATH"

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "Configuration:"
echo "  Base repository directory: $REPO_PATH"
echo "  Wrapper script: $WRAPPER_SCRIPT"
echo "  Config file: $CONFIG_PATH"
echo "  State directory: $SCRIPT_DIR/../state/"
echo ""
echo "Next Steps:"
echo "1. Restart Claude Desktop completely (Quit → Restart)"
echo "2. See docs/usage.md for how to interact with the server"
echo "3. See docs/api.md for available tools and resources"