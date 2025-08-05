#!/usr/bin/env python3
"""
Diff processing utilities for Git MCP Server
Handles different update modes and file content processing
"""
import difflib
import logging
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class UpdateMode(Enum):
    DIFFS_ONLY = "diffs_only"
    FULL_CONTENT = "full_content"
    CHANGED_FILES_ONLY = "changed_files_only"
    SMART = "smart"


class DiffProcessor:
    def __init__(self):
        pass

    def generate_diff(self, old_content: str, new_content: str, file_path: str) -> str:
        """Generate unified diff between old and new content"""
        return ''.join(difflib.unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            n=3
        ))

    def process_file_for_mode(self, file_path: str, current_content: str,
                              current_hash: str, old_content: str, old_hash: str,
                              update_mode: UpdateMode) -> Dict:
        """Process a single file according to update mode"""

        has_changed = current_hash != old_hash
        is_new_file = not old_hash

        result = {
            'file': file_path,
            'size': len(current_content),
            'changed': has_changed,
            'hash': current_hash
        }

        if update_mode == UpdateMode.FULL_CONTENT:
            result['content'] = current_content
            result['status'] = 'full_content'

        elif update_mode == UpdateMode.DIFFS_ONLY:
            if has_changed:
                if is_new_file:
                    result['content'] = current_content[:2000] + (
                        '...\n[truncated]' if len(current_content) > 2000 else ''
                    )
                    result['status'] = 'new_file'
                else:
                    diff = self.generate_diff(old_content, current_content, file_path)
                    if diff:
                        result['diff'] = diff
                        result['status'] = 'modified'
                    else:
                        result['status'] = 'no_changes'
            else:
                result['status'] = 'unchanged'

        elif update_mode == UpdateMode.CHANGED_FILES_ONLY:
            if has_changed:
                result['content'] = current_content
                result['status'] = 'changed'
                return result
            else:
                # Skip unchanged files
                return None

        elif update_mode == UpdateMode.SMART:
            if has_changed:
                if is_new_file:
                    # Full content for new files
                    result['content'] = current_content
                    result['status'] = 'new_file'
                else:
                    # Diff for modified files
                    diff = self.generate_diff(old_content, current_content, file_path)
                    if diff:
                        result['diff'] = diff
                        result['status'] = 'modified'
                    else:
                        result['status'] = 'no_changes'
            else:
                result['status'] = 'unchanged'

        return result

    def process_files_batch(self, file_data: List[Dict], update_mode: str) -> Dict:
        """Process multiple files according to update mode"""
        try:
            mode = UpdateMode(update_mode)
        except ValueError:
            mode = UpdateMode.SMART
            logger.warning(f"Unknown update mode '{update_mode}', using 'smart'")

        results = []
        changes_count = 0

        for file_info in file_data:
            file_path = file_info['path']
            current_content = file_info['current_content']
            current_hash = file_info['current_hash']
            old_content = file_info.get('old_content', '')
            old_hash = file_info.get('old_hash', '')

            processed_file = self.process_file_for_mode(
                file_path, current_content, current_hash,
                old_content, old_hash, mode
            )

            if processed_file:  # Some modes might return None for unchanged files
                results.append(processed_file)
                if processed_file.get('changed', False):
                    changes_count += 1

        return {
            'files': results,
            'update_mode': update_mode,
            'summary': {
                'total_processed': len(results),
                'changed_files': changes_count,
                'mode_description': self.get_mode_description(mode)
            }
        }

    def get_mode_description(self, mode: UpdateMode) -> str:
        """Get human-readable description of update mode"""
        descriptions = {
            UpdateMode.DIFFS_ONLY: "Shows unified diffs for changed files, full content for new files",
            UpdateMode.FULL_CONTENT: "Shows complete content of all files",
            UpdateMode.CHANGED_FILES_ONLY: "Shows only files that have changed",
            UpdateMode.SMART: "Shows diffs for modified files, full content for new files"
        }
        return descriptions.get(mode, "Unknown mode")

    def truncate_content(self, content: str, max_length: int = 2000) -> str:
        """Truncate content if too long"""
        if len(content) <= max_length:
            return content

        return content[:max_length] + f'\n\n... [truncated {len(content) - max_length} characters]'