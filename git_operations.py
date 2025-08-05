#!/usr/bin/env python3
"""
Git operations for Git MCP Server
Handles git-specific operations like status, commit history, etc.
"""
import json
import logging
from typing import Dict, List, Optional
from git import Repo

logger = logging.getLogger(__name__)


class GitOperations:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        try:
            self.repo = Repo(repo_path)
            logger.info(f"GitOperations initialized for {repo_path}")
        except Exception as e:
            logger.error(f"Failed to initialize git repo: {e}")
            self.repo = None

    async def get_status(self) -> str:
        """Get git repository status"""
        if not self.repo:
            return json.dumps({"error": "Git repository not available"})

        try:
            status = {
                "branch": self.repo.active_branch.name if self.repo.active_branch else "detached",
                "is_dirty": self.repo.is_dirty(),
                "untracked_files": self.repo.untracked_files[:10],  # Limit for efficiency
                "modified_files": [item.a_path for item in self.repo.index.diff(None)][:10],
                "staged_files": [item.a_path for item in self.repo.index.diff("HEAD")][:10],
                "note": "Lists limited to 10 items for efficiency"
            }
            return json.dumps(status, indent=2)
        except Exception as e:
            logger.error(f"Failed to get git status: {e}")
            return json.dumps({"error": str(e)})

    async def get_commit_history(self, limit: int = 10, branch: str = "main") -> List[Dict]:
        """Get commit history"""
        if not self.repo:
            return [{"error": "Git repository not available"}]

        try:
            commits = list(self.repo.iter_commits(branch, max_count=limit))
            return [{
                "commit_id": commit.hexsha[:8],
                "full_commit_id": commit.hexsha,
                "message": commit.message.strip(),
                "author": commit.author.name,
                "email": commit.author.email,
                "date": commit.committed_datetime.isoformat(),
                "files_changed": len(commit.stats.files)
            } for commit in commits]
        except Exception as e:
            logger.error(f"Failed to get commit history: {e}")
            return [{"error": f"Failed to get commit history: {str(e)}"}]

    async def get_branches(self) -> List[str]:
        """Get list of branches"""
        if not self.repo:
            return []

        try:
            return [branch.name for branch in self.repo.branches]
        except Exception as e:
            logger.error(f"Failed to get branches: {e}")
            return []

    async def get_remote_info(self) -> Dict:
        """Get remote repository information"""
        if not self.repo:
            return {"error": "Git repository not available"}

        try:
            remotes = []
            for remote in self.repo.remotes:
                remote_info = {
                    "name": remote.name,
                    "url": list(remote.urls)[0] if remote.urls else "No URL",
                    "fetch_info": [],
                    "push_info": []
                }

                # Get fetch and push URLs if different
                if hasattr(remote, 'urls'):
                    urls = list(remote.urls)
                    if len(urls) > 1:
                        remote_info["push_url"] = urls[1]

                remotes.append(remote_info)

            return {
                "remotes": remotes,
                "default_remote": remotes[0]["name"] if remotes else None,
                "total_remotes": len(remotes)
            }
        except Exception as e:
            logger.error(f"Failed to get remote info: {e}")
            return {"error": f"Failed to get remote info: {str(e)}"}

    async def get_file_history(self, file_path: str, limit: int = 10) -> List[Dict]:
        """Get commit history for a specific file"""
        if not self.repo:
            return [{"error": "Git repository not available"}]

        try:
            commits = list(self.repo.iter_commits(paths=file_path, max_count=limit))
            history = []

            for commit in commits:
                commit_info = {
                    "commit_id": commit.hexsha[:8],
                    "full_commit_id": commit.hexsha,
                    "message": commit.message.strip(),
                    "author": commit.author.name,
                    "email": commit.author.email,
                    "date": commit.committed_datetime.isoformat(),
                    "file_path": file_path
                }

                # Try to get file stats for this commit
                try:
                    if file_path in commit.stats.files:
                        stats = commit.stats.files[file_path]
                        commit_info["insertions"] = stats.get("insertions", 0)
                        commit_info["deletions"] = stats.get("deletions", 0)
                except:
                    pass

                history.append(commit_info)

            return history
        except Exception as e:
            logger.error(f"Failed to get file history for {file_path}: {e}")
            return [{"error": f"Failed to get file history: {str(e)}"}]

    async def get_diff_between_commits(self, commit1: str, commit2: str, file_path: Optional[str] = None) -> Dict:
        """Get diff between two commits"""
        if not self.repo:
            return {"error": "Git repository not available"}

        try:
            commit_obj1 = self.repo.commit(commit1)
            commit_obj2 = self.repo.commit(commit2)

            if file_path:
                diff = commit_obj1.diff(commit_obj2, paths=[file_path])
            else:
                diff = commit_obj1.diff(commit_obj2)

            diff_data = {
                "commit1": {
                    "id": commit1,
                    "message": commit_obj1.message.strip(),
                    "author": commit_obj1.author.name,
                    "date": commit_obj1.committed_datetime.isoformat()
                },
                "commit2": {
                    "id": commit2,
                    "message": commit_obj2.message.strip(),
                    "author": commit_obj2.author.name,
                    "date": commit_obj2.committed_datetime.isoformat()
                },
                "files_changed": len(diff),
                "changes": []
            }

            for item in diff[:20]:  # Limit for efficiency
                change_info = {
                    "file_path": item.a_path or item.b_path,
                    "change_type": item.change_type,
                    "a_blob_id": item.a_blob.hexsha if item.a_blob else None,
                    "b_blob_id": item.b_blob.hexsha if item.b_blob else None,
                    "diff_text": item.diff.decode('utf-8', errors='ignore')[:1000] if item.diff else None
                    # Truncate for efficiency
                }
                diff_data["changes"].append(change_info)

            if len(diff) > 20:
                diff_data["note"] = f"Showing first 20 of {len(diff)} changed files"

            return diff_data
        except Exception as e:
            logger.error(f"Failed to get diff between commits: {e}")
            return {"error": f"Failed to get diff: {str(e)}"}

    async def get_tags(self) -> List[Dict]:
        """Get repository tags with metadata"""
        if not self.repo:
            return [{"error": "Git repository not available"}]

        try:
            tags = []
            for tag in self.repo.tags:
                tag_info = {
                    "name": tag.name,
                    "commit_id": tag.commit.hexsha[:8],
                    "full_commit_id": tag.commit.hexsha,
                    "message": tag.commit.message.strip(),
                    "author": tag.commit.author.name,
                    "date": tag.commit.committed_datetime.isoformat()
                }

                # Check if it's an annotated tag
                try:
                    if hasattr(tag.tag, 'message'):
                        tag_info["tag_message"] = tag.tag.message
                        tag_info["tagger"] = tag.tag.tagger.name if tag.tag.tagger else None
                        tag_info["tag_date"] = tag.tag.tagged_date
                        tag_info["annotated"] = True
                    else:
                        tag_info["annotated"] = False
                except:
                    tag_info["annotated"] = False

                tags.append(tag_info)

            # Sort by date, newest first
            tags.sort(key=lambda x: x["date"], reverse=True)
            return tags
        except Exception as e:
            logger.error(f"Failed to get tags: {e}")
            return [{"error": f"Failed to get tags: {str(e)}"}]

    async def get_stash_list(self) -> List[Dict]:
        """Get stashed changes information"""
        if not self.repo:
            return [{"error": "Git repository not available"}]

        try:
            stashes = []
            for i, stash in enumerate(self.repo.git.stash("list").split('\n')):
                if stash.strip():
                    # Parse stash entry: stash@{0}: WIP on branch: message
                    parts = stash.split(': ', 2)
                    if len(parts) >= 2:
                        stash_info = {
                            "index": i,
                            "stash_ref": parts[0],
                            "description": parts[1] if len(parts) > 1 else "",
                            "message": parts[2] if len(parts) > 2 else "",
                            "raw": stash
                        }
                        stashes.append(stash_info)

            return stashes
        except Exception as e:
            logger.error(f"Failed to get stash list: {e}")
            return [{"error": f"Failed to get stash list: {str(e)}"}]

    async def get_repo_stats(self) -> Dict:
        """Get repository statistics and metrics"""
        if not self.repo:
            return {"error": "Git repository not available"}

        try:
            # Get basic repo info
            stats = {
                "repo_path": self.repo_path,
                "is_bare": self.repo.bare,
                "is_dirty": self.repo.is_dirty(),
                "head_is_detached": self.repo.head.is_detached,
                "active_branch": self.repo.active_branch.name if not self.repo.head.is_detached else None
            }

            # Count commits
            try:
                commit_count = sum(1 for _ in self.repo.iter_commits())
                stats["total_commits"] = commit_count
            except:
                stats["total_commits"] = "Unable to count"

            # Count branches
            stats["local_branches"] = len(list(self.repo.branches))

            # Count remotes
            stats["remotes"] = len(list(self.repo.remotes))

            # Count tags
            stats["tags"] = len(list(self.repo.tags))

            # Count stashes
            try:
                stash_count = len(self.repo.git.stash("list").split('\n')) if self.repo.git.stash("list") else 0
                stats["stashes"] = stash_count
            except:
                stats["stashes"] = 0

            # Working tree status
            stats["untracked_files"] = len(self.repo.untracked_files)
            stats["modified_files"] = len([item.a_path for item in self.repo.index.diff(None)])
            stats["staged_files"] = len([item.a_path for item in self.repo.index.diff("HEAD")])

            # Repository size (approximate)
            try:
                import os
                git_dir_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                                   for dirpath, dirnames, filenames in os.walk(self.repo.git_dir)
                                   for filename in filenames)
                stats["git_dir_size_bytes"] = git_dir_size
                stats["git_dir_size_mb"] = round(git_dir_size / (1024 * 1024), 2)
            except:
                stats["git_dir_size_bytes"] = "Unable to calculate"

            return stats
        except Exception as e:
            logger.error(f"Failed to get repo stats: {e}")
            return {"error": f"Failed to get repo stats: {str(e)}"}

    async def get_working_tree_status(self) -> Dict:
        """Get detailed working tree analysis"""
        if not self.repo:
            return {"error": "Git repository not available"}

        try:
            status = {
                "clean": not self.repo.is_dirty() and not self.repo.untracked_files,
                "summary": {
                    "untracked": len(self.repo.untracked_files),
                    "modified": 0,
                    "staged": 0,
                    "deleted": 0,
                    "renamed": 0
                },
                "files": {
                    "untracked": self.repo.untracked_files[:20],  # Limit for efficiency
                    "modified": [],
                    "staged": [],
                    "deleted": [],
                    "renamed": []
                }
            }

            # Analyze unstaged changes
            for item in self.repo.index.diff(None):
                if item.change_type == 'M':
                    status["files"]["modified"].append({
                        "path": item.a_path,
                        "change_type": "modified"
                    })
                    status["summary"]["modified"] += 1
                elif item.change_type == 'D':
                    status["files"]["deleted"].append({
                        "path": item.a_path,
                        "change_type": "deleted"
                    })
                    status["summary"]["deleted"] += 1

            # Analyze staged changes
            try:
                for item in self.repo.index.diff("HEAD"):
                    if item.change_type == 'M':
                        status["files"]["staged"].append({
                            "path": item.a_path,
                            "change_type": "modified"
                        })
                        status["summary"]["staged"] += 1
                    elif item.change_type == 'A':
                        status["files"]["staged"].append({
                            "path": item.a_path,
                            "change_type": "added"
                        })
                        status["summary"]["staged"] += 1
                    elif item.change_type == 'D':
                        status["files"]["staged"].append({
                            "path": item.a_path,
                            "change_type": "deleted"
                        })
                        status["summary"]["staged"] += 1
                    elif item.change_type == 'R':
                        status["files"]["renamed"].append({
                            "old_path": item.a_path,
                            "new_path": item.b_path,
                            "change_type": "renamed"
                        })
                        status["summary"]["renamed"] += 1
            except:
                # Might fail if there's no HEAD (empty repo)
                pass

            # Limit file lists for efficiency
            for file_type in status["files"]:
                if isinstance(status["files"][file_type], list) and len(status["files"][file_type]) > 20:
                    original_count = len(status["files"][file_type])
                    status["files"][file_type] = status["files"][file_type][:20]
                    status["files"][f"{file_type}_truncated"] = f"Showing first 20 of {original_count} files"

            return status
        except Exception as e:
            logger.error(f"Failed to get working tree status: {e}")
            return {"error": f"Failed to get working tree status: {str(e)}"}

    async def search_commits(self, query: str, search_type: str = "message", limit: int = 20) -> List[Dict]:
        """Search commits by message or author"""
        if not self.repo:
            return [{"error": "Git repository not available"}]

        try:
            commits = []
            search_query = query.lower()

            for commit in self.repo.iter_commits():
                match = False

                if search_type == "message":
                    match = search_query in commit.message.lower()
                elif search_type == "author":
                    match = search_query in commit.author.name.lower() or search_query in commit.author.email.lower()
                elif search_type == "both":
                    match = (search_query in commit.message.lower() or
                             search_query in commit.author.name.lower() or
                             search_query in commit.author.email.lower())

                if match:
                    commit_info = {
                        "commit_id": commit.hexsha[:8],
                        "full_commit_id": commit.hexsha,
                        "message": commit.message.strip(),
                        "author": commit.author.name,
                        "email": commit.author.email,
                        "date": commit.committed_datetime.isoformat(),
                        "files_changed": len(commit.stats.files),
                        "match_type": search_type
                    }
                    commits.append(commit_info)

                    if len(commits) >= limit:
                        break

            return commits
        except Exception as e:
            logger.error(f"Failed to search commits: {e}")
            return [{"error": f"Failed to search commits: {str(e)}"}]