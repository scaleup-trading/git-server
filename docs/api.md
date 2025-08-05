# API Reference

This document lists the tools and resources available in the Multi-Repository Git MCP Server.

## Tools

### Repository Management
- **`set_repository <repo_name>`**: Switch to a different repository.
  - Example: `set_repository my-website`
- **`list_repositories`**: List all available repositories in `/repos`.

### Workspace Management
- **`create_workspace <name> with files: <file_list>`**: Create a workspace with specified files.
  - Example: `create_workspace frontend with files: src/App.js, package.json`
- **`load_workspace <name> with <mode>`**: Load a workspace with the specified update mode (smart, diffs_only, full_content, changed_files_only).
  - Example: `load_workspace frontend with smart mode`
- **`update_workspace <name> with <mode>`**: Update a workspace with changes.
  - Example: `update_workspace frontend with diffs only`
- **`list_workspaces`**: List all available workspaces.

### File Operations
- **`get_files <file_list> with <mode>`**: Retrieve specific files with the specified update mode.
  - Example: `get_files src/main.py, docs/README.md with full content`
- **`search_files <pattern>`**: Search for files matching a pattern.
  - Example: `search_files *.py`
- **`load_git_context`**: Load repository changes (use sparingly, high token usage).
  - Example: `load_git_context with max 30 files and diffs only mode`

### Git Operations
- **`get_commit_history`**: Retrieve the commit history of the current repository.
- **`reset_state`**: Reset the tracking state for the current repository.

## Resources
- **`git://repositories`**: List all discovered repositories.
- **`git://current`**: Show current repository information.
- **`git://status`**: Display Git repository status (requires a selected repository).
- **`git://summary`**: Provide a repository summary with file counts.

For usage examples, see [usage.md](usage.md).