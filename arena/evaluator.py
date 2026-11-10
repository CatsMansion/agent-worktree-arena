from __future__ import annotations

import subprocess
from pathlib import Path


def test_task(worktree: Path, command: str, timeout: int) -> dict:
    try:
        result = subprocess.run(command, cwd=worktree, shell=True, text=True,
                                capture_output=True, timeout=timeout)
        return {"command": command, "exit_code": result.returncode,
                "stdout": result.stdout, "stderr": result.stderr, "timed_out": False}
    except subprocess.TimeoutExpired as error:
        return {"command": command, "exit_code": 124, "stdout": error.stdout or "",
                "stderr": error.stderr or "", "timed_out": True}


def changes(worktree: Path) -> tuple[list[str], str]:
    subprocess.run(["git", "add", "-N", "--", "."], cwd=worktree, capture_output=True, text=True)
    status = subprocess.run(["git", "status", "--porcelain"], cwd=worktree,
                            capture_output=True, text=True, check=True).stdout
    paths = [line[3:] for line in status.splitlines() if len(line) > 3]
    diff = subprocess.run(["git", "diff", "--no-ext-diff", "--", "."], cwd=worktree,
                          capture_output=True, text=True, check=True).stdout
    return paths, diff


def overlapping_paths(results: list[dict]) -> list[str]:
    if len(results) < 2:
        return []
    seen: set[str] = set()
    overlap: set[str] = set()
    for result in results:
        for path in result["changed_paths"]:
            if path in seen:
                overlap.add(path)
            seen.add(path)
    return sorted(overlap)
