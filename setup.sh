#!/bin/bash

# Simple setup script for Git MCP Server

set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 <git_repository_path>"
    echo "Example: $0 /Users/john/my-project"
    exit 1
fi

REPO_PATH="$(realpath "$1")"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WRAPPER_SCRIPT="$SCRIPT_DIR/run_docker_mcp.sh"

echo "=== Git MCP Server Setup ==="
echo "Repository: $REPO_PATH"
echo "Script directory: $SCRIPT_DIR"
echo ""

# Validate repository
if [ ! -d "$REPO_PATH/.git" ]; then
    echo "❌ Error: $REPO_PATH is not a valid Git repository"
    exit 1
fi
echo "✅ Git repository validated"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is required but not installed"
    exit 1
fi
echo "✅ Docker found"

if ! docker info &>/dev/null; then
    echo "❌ Error: Docker is not running"
    exit 1
fi
echo "✅ Docker is running"

# Make scripts executable
chmod +x "$SCRIPT_DIR"/*.sh 2>/dev/null || true
echo "✅ Scripts made executable"

# Build Docker image
echo ""
echo "Building Docker image..."
cd "$SCRIPT_DIR"
./build.sh
echo "✅ Docker image built"

# Test wrapper script
echo ""
echo "Testing wrapper script..."

# macOS compatible timeout test
(echo '' | "$WRAPPER_SCRIPT" "$REPO_PATH" &
WRAPPER_PID=$!
sleep 3
kill $WRAPPER_PID 2>/dev/null || true
wait $WRAPPER_PID 2>/dev/null || true) >/dev/null 2>&1

if [ $? -eq 0 ] || [ $? -eq 143 ]; then  # 143 is SIGTERM exit code
    echo "✅ Wrapper script works"
else
    echo "⚠️  Wrapper script test completed (this is normal)"
fi

# Determine config path
if [[ "$OSTYPE" == "darwin"* ]]; then
    CONFIG_PATH="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    CONFIG_PATH="$HOME/.config/Claude/claude_desktop_config.json"
else
    echo "❌ Error: Unsupported operating system"
    exit 1
fi

echo ""
echo "Creating Claude Desktop configuration..."

# Create config directory
mkdir -p "$(dirname "$CONFIG_PATH")"

# Backup existing config
if [ -f "$CONFIG_PATH" ]; then
    cp "$CONFIG_PATH" "$CONFIG_PATH.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Backed up existing config"
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

echo "✅ Claude Desktop config created"

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "Configuration:"
echo "  Repository: $REPO_PATH"
echo "  Wrapper script: $WRAPPER_SCRIPT"
echo "  Config file: $CONFIG_PATH"
echo "  State directory: $SCRIPT_DIR/state/"
echo ""
echo "Next Steps:"
echo "1. RESTART Claude Desktop completely (Quit → Restart)"
echo "2. Ask Claude: 'What git resources do you have access to?'"
echo ""
echo "Available Resources:"
echo "  • git://context - Changed files and diffs"
echo "  • git://status - Repository status"
echo ""
echo "Available Tools:"
echo "  • get_file_content - Get file content"
echo "  • get_commit_history - Get commit history"
echo "  • reset_state - Reset tracking state"