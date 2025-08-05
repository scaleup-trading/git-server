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

The server is organized into focused modules for better maintainability:

```
git-mcp-server/
├── src/                       # Source code
│   ├── git_mcp_server.py     # Main server orchestration
│   ├── core/                 # Core functionality
│   │   ├── file_manager.py   # File operations and ignore patterns
│   │   ├── state_manager.py  # Persistent state management
│   │   ├── diff_processor.py # Content diffing and update modes
│   │   ├── workspace_manager.py # Workspace creation and management
│   │   ├── git_operations.py # Git-specific operations
│   │   └── repository_manager.py # Multi-repository management
├── scripts/                   # Build and run scripts
│   ├── run_docker_mcp.sh     # Docker wrapper script
│   ├── build.sh              # Build Docker image
│   ├── setup.sh              # One-command setup
│   └── test_mcp.sh           # Test script
├── config/                    # Configuration files
│   └── .mcpignore.example    # Example ignore patterns
├── tests/                     # Unit and integration tests
│   └── test_core.py          # Core functionality tests
├── docs/                      # Documentation
│   ├── installation.md       # Installation guide
│   ├── usage.md              # Usage examples and update modes
│   └── api.md                # API/tool reference
├── Dockerfile                 # Docker container configuration
├── requirements.txt           # Python dependencies
├── LICENSE                    # Creative Commons Attribution-NonCommercial 4.0 License
└── README.md                 # Project overview
```

### Module Responsibilities

- **`git_mcp_server.py`**: Main MCP server, handles protocol and tool routing
- **`file_manager.py`**: File I/O, ignore patterns, file discovery and filtering
- **`state_manager.py`**: Persistent state storage for files and workspaces
- **`diff_processor.py`**: Content diffing with multiple update modes
- **`workspace_manager.py`**: Workspace creation, loading, and management
- **`git_operations.py`**: Git status, commit history, branch info
- **`repository_manager.py`**: Multi-repo discovery and switching

## 🚀 Getting Started

See [docs/installation.md](docs/installation.md) for detailed setup instructions, including cloning the repository, installing dependencies, and running with Docker.

## 🎛️ Usage and Tools

Refer to [docs/usage.md](docs/usage.md) for usage examples, workflows, and update modes, and [docs/api.md](docs/api.md) for a complete list of available tools and resources.

## 🔧 Configuration

### Custom Ignore Patterns
Create a `.mcpignore` file in your repository root to define custom ignore patterns. Use [config/.mcpignore.example](config/.mcpignore.example) as a template:
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

See [docs/installation.md](docs/installation.md) for instructions on building the Docker image and deploying the server.

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