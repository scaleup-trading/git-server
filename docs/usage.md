# Usage Guide

This guide covers how to use the Multi-Repository Git MCP Server with Claude Desktop, including workflows and update modes.

## Basic Usage
Interact with the server via Claude Desktop’s interface. Example commands:

```
You: What git repositories are available?
Claude: [Lists all discovered repositories in /repos]

You: Set repository to my-website
Claude: ✅ Switched to my-website

You: Create workspace "frontend" with files: src/App.js, src/Header.js, package.json
Claude: ✅ Created workspace with full content of 3 files

You: Update workspace "frontend" with diffs only
Claude: [Shows only changes since last update]
```

## Update Modes
Control how file changes are sent to Claude:

### `smart` (Default)
- **New files**: Full content
- **Modified files**: Unified diffs
- **Unchanged files**: Status only
- **Best for**: Balancing context and efficiency

### `diffs_only`
- **All changes**: Unified diffs only
- **New files**: Truncated content
- **Best for**: Minimal token usage

### `full_content`
- **All files**: Complete content
- **Best for**: Maximum context, highest token usage

### `changed_files_only`
- **Only changed files**: Full content
- **Best for**: Focusing on modified files

## Workflows

### Focused Development
Set up a workspace for a specific feature:
```bash
You: Set repository to backend-api
You: Create workspace "auth-feature" with files: src/auth.py, tests/test_auth.py, requirements.txt
You: Update workspace "auth-feature" with diffs only
Claude: [Shows changes made since last update]
```

Switch contexts:
```bash
You: Set repository to frontend
You: Load workspace "components" with smart mode
Claude: [Shows updated components with intelligent diff/content mix]
```

### Code Review
Review changes across a repository:
```bash
You: Set repository to my-project
You: Load git context with max 30 files and diffs only mode
Claude: [Shows changed files with diffs]

You: Get files src/main.py, docs/README.md with full content
Claude: [Shows complete content of specified files]
```

### Multi-Repository Work
Work on multiple repositories in parallel:
```bash
# Chat 1: Backend
You: Set repository to api-server
You: Create workspace "endpoints" with files: src/endpoints.py, tests/test_endpoints.py

# Chat 2: Frontend
You: Set repository to web-app
You: Create workspace "ui-components" with files: src/App.js, src/Button.js
```
Each session maintains separate state and context.

For tool details, see [api.md](api.md).