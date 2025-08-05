#!/usr/bin/env python3
"""
File management utilities for Git MCP Server
Handles file operations, ignore patterns, and hashing
"""
import os
import hashlib
import logging
import fnmatch
import subprocess
from typing import List, Optional

logger = logging.getLogger(__name__)


class FileManager:
    def __init__(self, repo_path: str):
        self.repo_path = os.path.abspath(repo_path)
        self.ignore_patterns = self.load_ignore_patterns()
        logger.info(f"FileManager initialized for {self.repo_path}")
        logger.info(f"Loaded {len(self.ignore_patterns)} ignore patterns")

    def load_ignore_patterns(self) -> List[str]:
        """Load patterns from .gitignore, .dockerignore, and .mcpignore"""
        patterns = []
        ignore_files = ['.gitignore', '.dockerignore', '.mcpignore']

        for ignore_file in ignore_files:
            file_path = os.path.join(self.repo_path, ignore_file)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                patterns.append(line)
                    logger.info(f"Loaded patterns from {ignore_file}")
                except Exception as e:
                    logger.warning(f"Failed to read {ignore_file}: {e}")

        # Add common patterns that should always be ignored for MCP
        default_patterns = [
            '.git/', '.git/**', '__pycache__/', '__pycache__/**', '*.pyc',
            '*.pyo', '*.pyd', '.Python', 'node_modules/', 'node_modules/**',
            '.env', '.DS_Store', 'Thumbs.db', '*.log', '.vscode/', '.idea/'
        ]
        patterns.extend(default_patterns)

        return patterns

    def is_ignored(self, file_path: str) -> bool:
        """Check if a file should be ignored based on patterns"""
        rel_path = os.path.relpath(file_path, self.repo_path)

        for pattern in self.ignore_patterns:
            # Handle directory patterns
            if pattern.endswith('/'):
                if rel_path.startswith(pattern[:-1] + '/') or rel_path == pattern[:-1]:
                    return True
            # Handle glob patterns
            elif fnmatch.fnmatch(rel_path, pattern):
                return True
            # Handle exact matches
            elif rel_path == pattern:
                return True
            # Handle path contains pattern
            elif '/' not in pattern and pattern in os.path.basename(rel_path):
                return True

        return False

    def get_repo_files(self, include_ignored: bool = False) -> List[str]:
        """Get tracked files in repository, optionally filtering ignored files"""
        try:
            result = subprocess.check_output(
                ['git', 'ls-files'],
                cwd=self.repo_path,
                text=True
            )
            files = [f.strip() for f in result.splitlines() if f.strip()]

            if not include_ignored:
                original_count = len(files)
                files = [f for f in files if not self.is_ignored(os.path.join(self.repo_path, f))]
                logger.info(f"Filtered {original_count} files to {len(files)} non-ignored files")

            return files
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get repo files: {e}")
            return []

    def calculate_file_hash(self, file_path: str) -> Optional[str]:
        """Calculate SHA256 hash of file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Failed to hash {file_path}: {e}")
            return None

    def read_file_content(self, file_path: str) -> Optional[str]:
        """Read file content safely"""
        full_path = os.path.join(self.repo_path, file_path)
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read {full_path}: {e}")
            return None

    def file_exists(self, file_path: str) -> bool:
        """Check if file exists in repository"""
        full_path = os.path.join(self.repo_path, file_path)
        return os.path.exists(full_path)

    def get_file_stats(self, file_path: str) -> dict:
        """Get file statistics"""
        full_path = os.path.join(self.repo_path, file_path)
        try:
            stat = os.stat(full_path)
            return {
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'exists': True
            }
        except Exception:
            return {'exists': False}

    def search_files(self, pattern: str, limit: int = 20) -> List[str]:
        """Search for files by pattern"""
        repo_files = self.get_repo_files(include_ignored=False)
        matches = []

        for file_path in repo_files:
            # Support different matching styles
            if (fnmatch.fnmatch(file_path, pattern) or
                    fnmatch.fnmatch(os.path.basename(file_path), pattern) or
                    pattern.lower() in file_path.lower()):

                matches.append(file_path)
                if len(matches) >= limit:
                    break

        return matches