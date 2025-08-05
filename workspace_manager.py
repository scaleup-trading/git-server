#!/usr/bin/env python3
"""
Workspace management for Git MCP Server
Handles workspace creation, loading, and updates
"""
import logging
from typing import Dict, List, Optional
from file_manager import FileManager
from state_manager import StateManager
from diff_processor import DiffProcessor

logger = logging.getLogger(__name__)


class WorkspaceManager:
    def __init__(self, file_manager: FileManager, state_manager: StateManager):
        self.file_manager = file_manager
        self.state_manager = state_manager
        self.diff_processor = DiffProcessor()

    async def create_workspace(self, name: str, file_paths: List[str], description: str = "") -> Dict:
        """Create a new workspace with specified files"""
        logger.info(f"Creating workspace '{name}' with {len(file_paths)} files")

        # Validate files
        valid_files = []
        invalid_files = []

        for file_path in file_paths:
            if not self.file_manager.file_exists(file_path):
                invalid_files.append({"file": file_path, "reason": "File not found"})
            elif self.file_manager.is_ignored(self.file_manager.repo_path + "/" + file_path):
                invalid_files.append({"file": file_path, "reason": "File is ignored"})
            else:
                valid_files.append(file_path)

        if not valid_files:
            return {
                "error": "No valid files provided",
                "invalid_files": invalid_files
            }

        # Create workspace in state
        result = self.state_manager.create_workspace(name, valid_files, description)
        if "error" in result:
            return result

        # Load initial content and create workspace state
        workspace_files = []
        for file_path in valid_files:
            content = self.file_manager.read_file_content(file_path)
            if content is not None:
                file_hash = self.file_manager.calculate_file_hash(
                    self.file_manager.repo_path + "/" + file_path
                )

                # Update workspace state
                self.state_manager.update_file_state(
                    file_path, file_hash, content, workspace_name=name
                )

                workspace_files.append({
                    'file': file_path,
                    'content': content,
                    'size': len(content),
                    'status': 'added_to_workspace'
                })
            else:
                invalid_files.append({"file": file_path, "reason": "Failed to read file"})

        return {
            'workspace_name': name,
            'description': description,
            'files_added': len(workspace_files),
            'invalid_files': invalid_files,
            'files': workspace_files,
            'message': f"Workspace '{name}' created with {len(workspace_files)} files"
        }

    async def load_workspace(self, name: str, update_mode: str = "smart") -> Dict:
        """Load a workspace with specified update mode"""
        logger.info(f"Loading workspace '{name}' with update_mode: {update_mode}")

        workspace = self.state_manager.get_workspace(name)
        if not workspace:
            available = [w['name'] for w in self.state_manager.list_workspaces()]
            return {
                "error": f"Workspace '{name}' not found",
                "available_workspaces": available
            }

        file_paths = workspace['files']
        return await self._process_workspace_files(name, file_paths, update_mode)

    async def update_workspace(self, name: str, update_mode: str = "diffs_only") -> Dict:
        """Update workspace with current file states"""
        logger.info(f"Updating workspace '{name}' with update_mode: {update_mode}")

        workspace = self.state_manager.get_workspace(name)
        if not workspace:
            return {"error": f"Workspace '{name}' not found"}

        file_paths = workspace['files']
        result = await self._process_workspace_files(name, file_paths, update_mode)

        # Update workspace state with new file states
        if 'files' in result:
            for file_info in result['files']:
                if 'error' not in file_info and file_info.get('changed', False):
                    file_path = file_info['file']
                    content = self.file_manager.read_file_content(file_path)
                    if content:
                        file_hash = file_info.get('hash')
                        self.state_manager.update_file_state(
                            file_path, file_hash, content, workspace_name=name
                        )

        return result

    async def _process_workspace_files(self, workspace_name: str, file_paths: List[str],
                                       update_mode: str) -> Dict:
        """Process workspace files according to update mode"""
        file_data = []

        for file_path in file_paths:
            if not self.file_manager.file_exists(file_path):
                file_data.append({
                    'file': file_path,
                    'error': 'File not found'
                })
                continue

            if self.file_manager.is_ignored(self.file_manager.repo_path + "/" + file_path):
                file_data.append({
                    'file': file_path,
                    'error': 'File is ignored'
                })
                continue

            # Get current file state
            current_content = self.file_manager.read_file_content(file_path)
            if current_content is None:
                file_data.append({
                    'file': file_path,
                    'error': 'Failed to read file'
                })
                continue

            current_hash = self.file_manager.calculate_file_hash(
                self.file_manager.repo_path + "/" + file_path
            )

            # Get stored state
            stored_state = self.state_manager.get_file_state(file_path, workspace_name)
            old_content = stored_state.get('content', '')
            old_hash = stored_state.get('hash', '')

            file_data.append({
                'path': file_path,
                'current_content': current_content,
                'current_hash': current_hash,
                'old_content': old_content,
                'old_hash': old_hash
            })

        # Process files with diff processor
        result = self.diff_processor.process_files_batch(file_data, update_mode)

        # Add workspace context
        result['workspace_name'] = workspace_name
        result['workspace_description'] = self.state_manager.get_workspace(workspace_name).get('description', '')

        return result

    async def list_workspaces(self) -> Dict:
        """List all workspaces"""
        workspaces = self.state_manager.list_workspaces()
        return {
            'workspaces': workspaces,
            'total': len(workspaces)
        }

    async def delete_workspace(self, name: str) -> Dict:
        """Delete a workspace"""
        success = self.state_manager.delete_workspace(name)
        if success:
            return {
                "message": f"Workspace '{name}' deleted successfully",
                "workspace_name": name
            }
        else:
            return {"error": f"Workspace '{name}' not found"}