from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class WorktreeError(RuntimeError):
    pass


def run_git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True)
    if check and result.returncode:
        raise WorktreeError(result.stderr.strip() or "git command failed")
    return result


def ensure_repository(repo: Path) -> None:
    if run_git(repo, "rev-parse", "--is-inside-work-tree", check=False).returncode:
        raise WorktreeError(f"{repo} is not a Git repository")
    if run_git(repo, "rev-parse", "--verify", "HEAD", check=False).returncode:
        raise WorktreeError("repository needs an initial commit before creating worktrees")


def worktree_root(repo: Path) -> Path:
    return repo / ".arena" / "worktrees"


def create(repo: Path, task_id: str) -> Path:
    ensure_repository(repo)
    target = worktree_root(repo) / task_id
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise WorktreeError(f"worktree already exists: {target}; use --clean first")
    run_git(repo, "worktree", "add", "--detach", str(target), "HEAD")
    return target


def remove(repo: Path, target: Path) -> None:
    root = worktree_root(repo).resolve()
    resolved = target.resolve()
    if root not in resolved.parents:
        raise WorktreeError("refusing to remove a path outside .arena/worktrees")
    run_git(repo, "worktree", "remove", "--force", str(resolved), check=False)
    if resolved.exists():
        shutil.rmtree(resolved)


def clean_all(repo: Path) -> None:
    root = worktree_root(repo)
    if not root.exists():
        return
    for child in root.iterdir():
        if child.is_dir():
            remove(repo, child)
    run_git(repo, "worktree", "prune", check=False)
