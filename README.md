# Multi-Repository Git MCP Server

A modular, efficient MCP (Model Context Protocol) server that provides Git repository context to Claude Desktop with support for multiple repositories, workspaces, and intelligent file tracking.

## 📜 License

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)**. You are free to use, copy, modify, and share this software for **personal, non-commercial purposes**, provided you give appropriate credit to the original author. **Commercial use, including selling the software or using it in commercial services, is prohibited** without explicit permission from the author. See the [LICENSE](LICENSE) file or [https://creativecommons.org/licenses/by-nc/4.0/](https://creativecommons.org/licenses/by-nc/4.0/) for full details.

### Usage Terms
- **Personal Use**: You can use, modify, and share the software for personal projects, research, or non-commercial purposes.
- **Attribution**: You must include the original copyright notice, a link to the license, and indicate if changes were made.
- **No Commercial Use**: You may not use this software for commercial purposes, such as selling it, offering it as part of a commercial service, or using it in a business to generate revenue, without permission from the author.
- **Contact for Commercial Use**: If you wish to use this software commercially, please contact [Your Contact Information] for licensing arrangements.

## 🎯 Key Features

- **Multi-Repository Support**: Dynamically switch between multiple git repositories
- **Workspace Management**: Create curated file sets for focused work
- **Intelligent File Tracking**: Persistent state with efficient diff-based updates
- **Flexible Update Modes**: Control how file changes are communicated to Claude
- **Smart File Filtering**: Respects .gitignore, .dockerignore, and .mcpignore patterns
- **Token Efficiency**: Only send what's needed when it's needed

## 📁 Modular Architecture

The server is now split into focused modules for better maintainability:

```
git-mcp-server/
├── git_mcp_server.py          # Main server orchestration
├── file_manager.py            # File operations and ignore patterns
├── state_manager.py           # Persistent state management
├── diff_processor.py          # Content diffing and update modes
├── workspace_manager.py       # Workspace creation and management
├── git_operations.py          # Git-specific operations
├── repository_manager.py      # Multi-repository management
├── Dockerfile                 # Docker container configuration
├── run_docker_mcp.sh         # Docker wrapper script
├── build.sh                  # Build Docker image
├── setup.sh                  # One-command setup
├── test_mcp.sh               # Test script
├── requirements.txt          # Python dependencies
├── LICENSE                    # Creative Commons Attribution-NonCommercial 4.0 License
└── README.md
```

### Module Responsibilities

- **`git_mcp_server.py`**: Main MCP server, handles protocol and tool routing
- **`file_manager.py`**: File I/O, ignore patterns, file discovery and filtering
- **`state_manager.py`**: Persistent state storage for files and workspaces
- **`diff_processor.py`**: Content diffing with multiple update modes
- **`workspace_manager.py`**: Workspace creation, loading, and management
- **`git_operations.py`**: Git status, commit history, branch info
- **`repository_manager.py`**: Multi-repo discovery and switching

## 🚀 Quick Start

### 1. Setup
```bash
# Clone/download this project
mkdir git-mcp-server && cd git-mcp-server

# Copy all the module files above

# Run setup with your projects directory
./setup.sh /Users/john/Projects

# Restart Claude Desktop
```

### 2. Basic Usage
```
You: What git repositories are available?
Claude: [Shows all discovered repositories]

You: Set repository to my-website
Claude: ✅ Switched to my-website

You: Create workspace "frontend" with files: src/App.js, src/Header.js, package.json
Claude: ✅ Created workspace with full content of 3 files

You: Update workspace "frontend" with diffs only
Claude: [Shows only changes since last time]
```

## 🎛️ Update Modes

Control how file changes are communicated:

### `smart` (Default)
- **New files**: Full content
- **Modified files**: Unified diffs
- **Unchanged files**: Status only
- **Best balance** of context and efficiency

### `diffs_only` (Most Efficient)
- **All changes**: Unified diffs only
- **New files**: Truncated content
- **Minimal token usage**

### `full_content` (Complete Context)
- **All files**: Complete content
- **Highest token usage**
- **Full context for Claude**

### `changed_files_only` (Changed Only)
- **Only changed files**: Full content
- **Skip unchanged files entirely**
- **Balanced approach**

## 🛠️ Available Tools

### Repository Management
- `set_repository` - Switch to a different repository
- `list_repositories` - List all available repositories

### Workspace Management
- `create_workspace` - Create curated file sets
- `load_workspace` - Load workspace with update mode
- `update_workspace` - Check for workspace updates
- `list_workspaces` - List all workspaces

### File Operations
- `get_files` - Get specific files with update control
- `search_files` - Search files by pattern
- `load_git_context` - Load repository changes (use sparingly)

### Git Operations
- `get_commit_history` - Get commit history
- `reset_state` - Reset tracking state

## 📊 Available Resources

- `git://repositories` - List all discovered repositories
- `git://current` - Current repository information
- `git://status` - Git repository status (when repo selected)
- `git://summary` - Repository summary with file counts

## 💡 Usage Examples

### Focused Development Workflow
```bash
# Set up workspace for specific feature
You: Set repository to backend-api
You: Create workspace "auth

-feature" with files: src/auth.py, tests/test_auth.py, requirements.txt

# Work on files... then check updates efficiently
You: Update workspace "auth-feature" with diffs only
Claude: [Shows only the changes you made]

# Switch context
You: Set repository to frontend
You: Load workspace "components" with smart mode
Claude: [Shows updated components with intelligent diff/content mix]
```

### Code Review Mode
```bash
You: Set repository to my-project
You: Load git context with max 30 files and diffs only mode
Claude: [Shows changed files across repository with diffs]

You: Get files src/main.py, docs/README.md with full content
Claude: [Shows complete content of specific files]
```

### Multi-Repository Work
```bash
# Chat 1: Work on backend
You: Set repository to api-server
You: Create workspace "endpoints" with files: [endpoint files]

# Chat 2: Work on frontend
You: Set repository to web-app
You: Create workspace "ui-components" with files: [component files]

# Each maintains separate state and context
```

## 🔧 Configuration

### Custom Ignore Patterns
Create `.mcpignore` in your repository root:
```
# Custom MCP ignores
build/
dist/
*.log
*.tmp
docs/generated/
coverage/
```

### Directory Structure
```
/Users/john/Projects/           # Base directory
├── api-server/                 # Git repo 1
├── web-app/                    # Git repo 2
├── mobile-app/                 # Git repo 3
└── docs-site/                  # Git repo 4
```

## 🏗️ Build & Deploy

```bash
# Build
./build.sh

# Test
./test_mcp.sh /Users/john/Projects

# Setup with Claude Desktop
./setup.sh /Users/john/Projects
```

## 🎯 Benefits

### For Token Efficiency
- **Workspace-based**: Only load files you're actively working on
- **Diff-based updates**: Send only changes, not entire files
- **Smart filtering**: Automatic ignore pattern respect
- **Persistent state**: Remember what Claude has seen

### For Developer Experience
- **Multi-repo support**: Switch between projects seamlessly
- **Flexible updates**: Choose how changes are communicated
- **Focused workspaces**: Create context for specific tasks
- **Persistent across sessions**: State survives Docker restarts

### For Code Quality
- **Modular architecture**: Easy to understand and maintain
- **Comprehensive logging**: Debug issues easily
- **Error handling**: Graceful failure recovery
- **Type hints**: Better code documentation

This modular architecture makes the codebase much more maintainable while providing powerful features for efficient repository management! 🎉