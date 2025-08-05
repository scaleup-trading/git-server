#!/usr/bin/env python3
"""
Repository management for Multi-Repo Git MCP Server
Handles repository discovery and switching
"""
import os
import json
import logging
from typing import List, Dict, Optional
from file_manager import FileManager
from state_manager import StateManager
from git_operations import GitOperations
from workspace_manager import WorkspaceManager

logger = logging.getLogger(__name__)


class RepositoryManager:
    def __init__(self, base_repos_dir: str, state_dir: str):
        self.base_repos_dir = os.path.abspath(base_repos_dir)
        self.state_dir = state_dir

        # Current repository components
        self.current_repo = None
        self.current_repo_path = None
        self.file_manager = None
        self.state_manager = None
        self.git_operations = None
        self.workspace_manager = None

        logger.info(f"RepositoryManager initialized for {self.base_repos_dir}")

    def discover_repositories(self) -> List[Dict]:
        """Discover all git repositories in the base directory"""
        repositories = []

        try:
            # Check if base_repos_dir itself is a git repo
            if os.path.exists(os.path.join(self.base_repos_dir, '.git')):
                repo_name = os.path.basename(self.base_repos_dir)
                repositories.append({
                    'name': repo_name,
                    'path': self.base_repos_dir,
                    'relative_path': '.',
                    'type': 'root'
                })

            # Look for git repositories in subdirectories
            if os.path.isdir(self.base_repos_dir):
                for item in os.listdir(self.base_repos_dir):
                    item_path = os.path.join(self.base_repos_dir, item)
                    if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, '.git')):
                        repositories.append({
                            'name': item,
                            'path': item_path,
                            'relative_path': item,
                            'type': 'subdirectory'
                        })
        except Exception as e:
            logger.error(f"Error discovering repositories: {e}")

        logger.info(f"Discovered {len(repositories)} git repositories")
        return repositories

    def set_current_repository(self, repo_name: str) -> Dict:
        """Set the current active repository"""
        repositories = self.discover_repositories()

        # Find repository by name
        repo_info = None
        for repo in repositories:
            if repo['name'] == repo_name:
                repo_info = repo
                break

        if not repo_info:
            return {
                "error": f"Repository '{repo_name}' not found",
                "available_repositories": [r['name'] for r in repositories]
            }

        # Validate it's actually a git repository
        repo_path = repo_info['path']
        if not os.path.exists(os.path.join(repo_path, '.git')):
            return {
                "error": f"'{repo_name}' is not a valid git repository",
                "path": repo_path
            }

        # Set current repository and initialize components
        self.current_repo = repo_name
        self.current_repo_path = repo_path

        # Initialize all components for the new repository
        self.file_manager = FileManager(repo_path)
        self.state_manager = StateManager(repo_name, repo_path, self.state_dir)
        self.git_operations = GitOperations(repo_path)
        self.workspace_manager = WorkspaceManager(self.file_manager, self.state_manager)

        logger.info(f"Switched to repository: {repo_name} at {repo_path}")

        return {
            "success": True,
            "repository": repo_name,
            "path": repo_path,
            "ignore_patterns_loaded": len(self.file_manager.ignore_patterns),
            "message": f"Switched to repository '{repo_name}'"
        }

    def get_current_info(self) -> Dict:
        """Get information about currently selected repository"""
        if not self.current_repo:
            return {
                "message": "No repository currently selected",
                "note": "Use 'set_repository' tool to select a repository"
            }

        return {
            "current_repository": self.current_repo,
            "repository_path": self.current_repo_path,
            "ignore_patterns_count": len(self.file_manager.ignore_patterns) if self.file_manager else 0
        }

    async def get_repository_summary(self) -> str:
        """Get repository summary without loading full context"""
        if not self.current_repo or not self.file_manager:
            return json.dumps({"error": "No repository selected"})

        all_files = self.file_manager.get_repo_files(include_ignored=True)
        filtered_files = self.file_manager.get_repo_files(include_ignored=False)
        state = self.state_manager.load_state()

        # Count file types
        file_types = {}
        for file_path in filtered_files:
            ext = os.path.splitext(file_path)[1] or 'no extension'
            file_types[ext] = file_types.get(ext, 0) + 1

        # Get git info
        try:
            status_json = await self.git_operations.get_status()
            status = json.loads(status_json)
            branch = status.get("branch", "unknown")
            is_dirty = status.get("is_dirty", False)
        except Exception:
            branch = "unknown"
            is_dirty = False

        summary = {
            "repository_name": self.current_repo,
            "repository_path": self.current_repo_path,
            "branch": branch,
            "is_dirty": is_dirty,
            "file_counts": {
                "total_tracked": len(all_files),
                "non_ignored": len(filtered_files),
                "ignored": len(all_files) - len(filtered_files),
                "tracked_in_state": len(state)
            },
            "file_types": dict(sorted(file_types.items(), key=lambda x: x[1], reverse=True)),
            "ignore_patterns_count": len(self.file_manager.ignore_patterns),
            "workspaces_count": len(self.state_manager.list_workspaces())
        }

        return json.dumps(summary, indent=2)

    def is_repository_selected(self) -> bool:
        """Check if a repository is currently selected"""
        return self.current_repo is not None

    def get_components(self) -> tuple:
        """Get all components for the current repository"""
        if not self.is_repository_selected():
            return None, None, None, None

        return (
            self.file_manager,
            self.state_manager,
            self.git_operations,
            self.workspace_manager
        )