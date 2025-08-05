#!/usr/bin/env python3
"""
Main Git MCP Server
Multi-repository MCP server with workspace management and efficient file tracking
"""
import os
import sys
import json
import logging
import asyncio
import traceback
from typing import List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent
from src.core.diff_processor import DiffProcessor
from src.core.repository_manager import RepositoryManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


class MultiRepoGitMCPServer:
    def __init__(self, base_repos_dir: str, state_dir: str = "/app/state"):
        self.server = Server("multi-git-context-server")
        self.state_dir = state_dir
        self.diff_processor = DiffProcessor()

        # Initialize repository manager
        self.repo_manager = RepositoryManager(base_repos_dir, state_dir)

        # Create state directory
        os.makedirs(state_dir, exist_ok=True)

        logger.info(f"Multi-Repo Git MCP Server initialized")
        logger.info(f"Base repos directory: {base_repos_dir}")
        logger.info(f"State directory: {state_dir}")

        self.setup_handlers()

    def setup_handlers(self):
        """Setup MCP server handlers"""

        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            logger.info("Listing resources")
            resources = [
                Resource(
                    uri="git://repositories",
                    name="Available Repositories",
                    description="List of available git repositories",
                    mimeType="application/json"
                ),
                Resource(
                    uri="git://current",
                    name="Current Repository Info",
                    description="Information about currently selected repository",
                    mimeType="application/json"
                )
            ]

            # Add repository-specific resources if a repo is selected
            if self.repo_manager.is_repository_selected():
                resources.extend([
                    Resource(
                        uri="git://status",
                        name="Git Status",
                        description="Current git repository status",
                        mimeType="application/json"
                    ),
                    Resource(
                        uri="git://summary",
                        name="Git Summary",
                        description="Repository summary with file counts",
                        mimeType="application/json"
                    )
                ])

            logger.info(f"Returning {len(resources)} resources")
            return resources

        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            logger.info(f"Reading resource: {uri}")
            uri_str = str(uri)

            try:
                if uri_str == "git://repositories":
                    repositories = self.repo_manager.discover_repositories()
                    return json.dumps({
                        "available_repositories": repositories,
                        "current_repository": self.repo_manager.current_repo,
                        "base_directory": self.repo_manager.base_repos_dir,
                        "total_found": len(repositories)
                    }, indent=2)

                elif uri_str == "git://current":
                    return json.dumps(self.repo_manager.get_current_info(), indent=2)

                elif uri_str == "git://status":
                    if not self.repo_manager.is_repository_selected():
                        raise ValueError("No repository selected. Use 'set_repository' tool first.")
                    _, _, git_ops, _ = self.repo_manager.get_components()
                    return await git_ops.get_status()

                elif uri_str == "git://summary":
                    if not self.repo_manager.is_repository_selected():
                        raise ValueError("No repository selected. Use 'set_repository' tool first.")
                    return await self.repo_manager.get_repository_summary()

                else:
                    logger.error(f"Unknown resource requested: {uri_str}")
                    raise ValueError(f"Unknown resource: {uri_str}")
            except Exception as e:
                logger.error(f"Exception in read_resource for {uri_str}: {e}")
                logger.error(traceback.format_exc())
                raise

        @self.server.list_prompts()
        async def list_prompts():
            return []

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            logger.info("Listing tools")
            tools = [
                Tool(
                    name="set_repository",
                    description="Set the active git repository to work with",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "repository_name": {
                                "type": "string",
                                "description": "Name of the repository to switch to"
                            }
                        },
                        "required": ["repository_name"]
                    }
                ),
                Tool(
                    name="list_repositories",
                    description="List all available git repositories",
                    inputSchema={"type": "object", "properties": {}}
                )
            ]

            # Add repository-specific tools if a repo is selected
            if self.repo_manager.is_repository_selected():
                tools.extend([
                    Tool(
                        name="create_workspace",
                        description="Create a curated workspace with specific files",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Workspace name"},
                                "file_paths": {"type": "array", "items": {"type": "string"},
                                               "description": "Files to include"},
                                "description": {"type": "string", "description": "Optional description"}
                            },
                            "required": ["name", "file_paths"]
                        }
                    ),
                    Tool(
                        name="load_workspace",
                        description="Load a workspace with specified update mode",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Workspace name"},
                                "update_mode": {
                                    "type": "string",
                                    "enum": ["diffs_only", "full_content", "changed_files_only", "smart"],
                                    "default": "smart",
                                    "description": "How to handle updates"
                                }
                            },
                            "required": ["name"]
                        }
                    ),
                    Tool(
                        name="update_workspace",
                        description="Update workspace with current file states",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Workspace name"},
                                "update_mode": {"type": "string",
                                                "enum": ["diffs_only", "full_content", "changed_files_only", "smart"],
                                                "default": "diffs_only"}
                            },
                            "required": ["name"]
                        }
                    ),
                    Tool(
                        name="list_workspaces",
                        description="List all workspaces for current repository",
                        inputSchema={"type": "object", "properties": {}}
                    ),
                    Tool(
                        name="get_files",
                        description="Get specific files with update mode control",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "file_paths": {"type": "array", "items": {"type": "string"},
                                               "description": "File paths"},
                                "update_mode": {"type": "string", "enum": ["diffs_only", "full_content", "smart"],
                                                "default": "smart"}
                            },
                            "required": ["file_paths"]
                        }
                    ),
                    Tool(
                        name="search_files",
                        description="Search for files by pattern",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "pattern": {"type": "string", "description": "Search pattern"},
                                "limit": {"type": "integer", "default": 20, "description": "Max results"}
                            },
                            "required": ["pattern"]
                        }
                    ),
                    Tool(
                        name="load_git_context",
                        description="Load git context (use sparingly for efficiency)",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "max_files": {"type": "integer", "default": 50, "description": "Max files to process"},
                                "update_mode": {"type": "string", "enum": ["diffs_only", "smart"], "default": "smart"}
                            }
                        }
                    ),
                    Tool(
                        name="get_commit_history",
                        description="Get commit history",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "limit": {"type": "integer", "default": 10},
                                "branch": {"type": "string", "default": "main"}
                            }
                        }
                    ),
                    Tool(
                        name="reset_state",
                        description="Reset state (main repo or specific workspace)",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "confirm": {"type": "boolean", "default": False},
                                "workspace_name": {"type": "string",
                                                   "description": "Optional: reset only this workspace"}
                            }
                        }
                    )
                ])

            return tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> List[TextContent]:
            logger.info(f"Calling tool: {name}")
            try:
                # Repository management tools
                if name == "set_repository":
                    result = self.repo_manager.set_current_repository(arguments["repository_name"])

                elif name == "list_repositories":
                    repositories = self.repo_manager.discover_repositories()
                    result = {
                        "repositories": repositories,
                        "current": self.repo_manager.current_repo,
                        "total": len(repositories)
                    }

                # Repository-specific tools
                elif name in ["create_workspace", "load_workspace", "update_workspace", "list_workspaces",
                              "get_files", "search_files", "load_git_context", "get_commit_history", "reset_state"]:

                    if not self.repo_manager.is_repository_selected():
                        result = {"error": "No repository selected. Use 'set_repository' tool first."}
                    else:
                        result = await self._handle_repository_tool(name, arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")

                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                logger.error(traceback.format_exc())
                raise

        logger.info("All MCP handlers registered successfully")

    async def _handle_repository_tool(self, name: str, arguments: dict) -> dict:
        """Handle repository-specific tool calls"""
        file_manager, state_manager, git_ops, workspace_manager = self.repo_manager.get_components()

        if name == "create_workspace":
            return await workspace_manager.create_workspace(
                arguments["name"],
                arguments["file_paths"],
                arguments.get("description", "")
            )

        elif name == "load_workspace":
            return await workspace_manager.load_workspace(
                arguments["name"],
                arguments.get("update_mode", "smart")
            )

        elif name == "update_workspace":
            return await workspace_manager.update_workspace(
                arguments["name"],
                arguments.get("update_mode", "diffs_only")
            )

        elif name == "list_workspaces":
            return await workspace_manager.list_workspaces()

        elif name == "get_files":
            return await self._get_files_with_mode(
                arguments["file_paths"],
                arguments.get("update_mode", "smart")
            )

        elif name == "search_files":
            matches = file_manager.search_files(
                arguments["pattern"],
                arguments.get("limit", 20)
            )
            return {
                "repository": self.repo_manager.current_repo,
                "pattern": arguments["pattern"],
                "matches": [{"file": f, **file_manager.get_file_stats(f)} for f in matches],
                "total_found": len(matches)
            }

        elif name == "load_git_context":
            return await self._load_git_context(
                arguments.get("max_files", 50),
                arguments.get("update_mode", "smart")
            )

        elif name == "get_commit_history":
            return await git_ops.get_commit_history(
                arguments.get("limit", 10),
                arguments.get("branch", "main")
            )

        elif name == "reset_state":
            if not arguments.get("confirm", False):
                return {
                    "message": "State reset requires confirmation",
                    "usage": "Set confirm=true to reset state"
                }

            workspace_name = arguments.get("workspace_name")
            success = state_manager.reset_state(workspace_name)

            if success:
                target = f"workspace '{workspace_name}'" if workspace_name else "repository state"
                return {"message": f"Successfully reset {target}"}
            else:
                return {"error": "Failed to reset state"}

    async def _get_files_with_mode(self, file_paths: List[str], update_mode: str) -> dict:
        """Get files with specified update mode"""
        file_manager, state_manager, _, _ = self.repo_manager.get_components()

        file_data = []
        for file_path in file_paths:
            if not file_manager.file_exists(file_path):
                file_data.append({"file": file_path, "error": "File not found"})
                continue

            if file_manager.is_ignored(file_manager.repo_path + "/" + file_path):
                file_data.append({"file": file_path, "error": "File is ignored"})
                continue

            current_content = file_manager.read_file_content(file_path)
            if current_content is None:
                file_data.append({"file": file_path, "error": "Failed to read file"})
                continue

            current_hash = file_manager.calculate_file_hash(file_manager.repo_path + "/" + file_path)
            stored_state = state_manager.get_file_state(file_path)
            old_content = stored_state.get('content', '')
            old_hash = stored_state.get('hash', '')

            file_data.append({
                'path': file_path,
                'current_content': current_content,
                'current_hash': current_hash,
                'old_content': old_content,
                'old_hash': old_hash
            })

            # Update state
            state_manager.update_file_state(file_path, current_hash, current_content)

        result = self.diff_processor.process_files_batch(file_data, update_mode)
        result['repository'] = self.repo_manager.current_repo
        return result

    async def _load_git_context(self, max_files: int, update_mode: str) -> dict:
        """Load git context with specified limits and update mode"""
        file_manager, state_manager, _, _ = self.repo_manager.get_components()

        repo_files = file_manager.get_repo_files(include_ignored=False)

        # Limit files for efficiency
        if len(repo_files) > max_files:
            logger.warning(f"Repository has {len(repo_files)} files, limiting to {max_files}")
            repo_files = repo_files[:max_files]

        file_data = []
        for file_path in repo_files:
            current_content = file_manager.read_file_content(file_path)
            if current_content is None:
                continue

            current_hash = file_manager.calculate_file_hash(file_manager.repo_path + "/" + file_path)
            stored_state = state_manager.get_file_state(file_path)
            old_content = stored_state.get('content', '')
            old_hash = stored_state.get('hash', '')

            # Only include changed files to reduce token usage
            if current_hash != old_hash:
                file_data.append({
                    'path': file_path,
                    'current_content': current_content,
                    'current_hash': current_hash,
                    'old_content': old_content,
                    'old_hash': old_hash
                })

                # Update state
                state_manager.update_file_state(file_path, current_hash, current_content)

        result = self.diff_processor.process_files_batch(file_data, update_mode)
        result.update({
            'repository': self.repo_manager.current_repo,
            'context': 'git_context_load',
            'summary': {
                **result.get('summary', {}),
                'total_files_in_repo': len(file_manager.get_repo_files(include_ignored=False)),
                'files_scanned': len(repo_files),
                'note': f'Limited to {max_files} files for efficiency' if len(repo_files) == max_files else None
            }
        })
        return result

    async def run(self):
        """Run the MCP server"""
        try:
            async with stdio_server() as streams:
                read_stream, write_stream = streams
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        except Exception as e:
            logger.error(f"Error running MCP server: {e}")
            logger.error(traceback.format_exc())
            raise


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 git_mcp_server.py <base_repos_directory>", file=sys.stderr)
        print("Example: python3 git_mcp_server.py /Users/john/Projects", file=sys.stderr)
        sys.exit(1)

    base_repos_dir = sys.argv[1]

    try:
        state_dir = "/app/state" if os.path.exists("/app") else "./state"
        server = MultiRepoGitMCPServer(base_repos_dir, state_dir)
        asyncio.run(server.run())
    except Exception as e:
        logger.error(f"Server failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()