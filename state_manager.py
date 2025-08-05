#!/usr/bin/env python3
"""
State management for Git MCP Server
Handles persistent state for file tracking and workspace management
"""
import os
import json
import hashlib
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class StateManager:
    def __init__(self, repo_name: str, repo_path: str, state_dir: str):
        self.repo_name = repo_name
        self.repo_path = repo_path
        self.state_dir = state_dir

        # Create unique identifiers
        repo_hash = hashlib.sha256(repo_path.encode()).hexdigest()[:12]
        self.state_file = os.path.join(state_dir, f"mcp_state_{repo_name}_{repo_hash}.json")
        self.workspaces_file = os.path.join(state_dir, f"workspaces_{repo_name}_{repo_hash}.json")

        # Ensure state directory exists
        os.makedirs(state_dir, exist_ok=True)

        logger.info(f"StateManager initialized for {repo_name}")
        logger.info(f"State file: {self.state_file}")
        logger.info(f"Workspaces file: {self.workspaces_file}")

    def load_state(self) -> Dict:
        """Load main repository state"""
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_state(self, state: Dict):
        """Save main repository state"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def load_workspaces(self) -> Dict:
        """Load workspaces configuration"""
        try:
            with open(self.workspaces_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_workspaces(self, workspaces: Dict):
        """Save workspaces configuration"""
        try:
            with open(self.workspaces_file, 'w') as f:
                json.dump(workspaces, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save workspaces: {e}")

    def reset_state(self, workspace_name: Optional[str] = None) -> bool:
        """Reset state - either main state or specific workspace"""
        try:
            if workspace_name:
                # Reset specific workspace
                workspaces = self.load_workspaces()
                if workspace_name in workspaces:
                    workspaces[workspace_name]['state'] = {}
                    self.save_workspaces(workspaces)
                    logger.info(f"Reset workspace '{workspace_name}' state")
                    return True
                else:
                    logger.error(f"Workspace '{workspace_name}' not found")
                    return False
            else:
                # Reset main state
                if os.path.exists(self.state_file):
                    os.remove(self.state_file)
                    logger.info("Reset main repository state")
                return True
        except Exception as e:
            logger.error(f"Failed to reset state: {e}")
            return False

    def get_file_state(self, file_path: str, workspace_name: Optional[str] = None) -> Dict:
        """Get state for a specific file"""
        if workspace_name:
            workspaces = self.load_workspaces()
            workspace = workspaces.get(workspace_name, {})
            return workspace.get('state', {}).get(file_path, {})
        else:
            state = self.load_state()
            return state.get(file_path, {})

    def update_file_state(self, file_path: str, file_hash: str, content: str,
                          workspace_name: Optional[str] = None):
        """Update state for a specific file"""
        file_state = {
            'hash': file_hash,
            'content': content,
            'size': len(content)
        }

        if workspace_name:
            workspaces = self.load_workspaces()
            if workspace_name in workspaces:
                if 'state' not in workspaces[workspace_name]:
                    workspaces[workspace_name]['state'] = {}
                workspaces[workspace_name]['state'][file_path] = file_state
                self.save_workspaces(workspaces)
        else:
            state = self.load_state()
            state[file_path] = file_state
            self.save_state(state)

    def create_workspace(self, name: str, file_paths: List[str], description: str = "") -> Dict:
        """Create a new workspace"""
        workspaces = self.load_workspaces()

        if name in workspaces:
            return {"error": f"Workspace '{name}' already exists"}

        import time
        workspaces[name] = {
            'description': description,
            'files': file_paths,
            'created_at': time.time(),
            'state': {}
        }

        self.save_workspaces(workspaces)
        logger.info(f"Created workspace '{name}' with {len(file_paths)} files")

        return {
            "success": True,
            "workspace_name": name,
            "file_count": len(file_paths)
        }

    def get_workspace(self, name: str) -> Optional[Dict]:
        """Get workspace by name"""
        workspaces = self.load_workspaces()
        return workspaces.get(name)

    def list_workspaces(self) -> List[Dict]:
        """List all workspaces"""
        workspaces = self.load_workspaces()

        workspace_list = []
        for name, config in workspaces.items():
            workspace_list.append({
                'name': name,
                'description': config.get('description', ''),
                'file_count': len(config.get('files', [])),
                'created_at': config.get('created_at', 0)
            })

        return workspace_list

    def delete_workspace(self, name: str) -> bool:
        """Delete a workspace"""
        workspaces = self.load_workspaces()
        if name in workspaces:
            del workspaces[name]
            self.save_workspaces(workspaces)
            logger.info(f"Deleted workspace '{name}'")
            return True
        return False