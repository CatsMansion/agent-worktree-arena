from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RunResult:
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool = False


def demo_runner(worktree: Path, task: dict, timeout: int) -> RunResult:
    """A deterministic, offline runner for demos and tests."""
    output = worktree / task["expected_file"]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(task["expected_content"], encoding="utf-8")
    return RunResult(0, f"demo wrote {output.relative_to(worktree)}\n", "")


def command_runner(worktree: Path, task: dict, command_template: str, timeout: int) -> RunResult:
    command = command_template.format(prompt=task["prompt"], task_id=task["id"])
    try:
        completed = subprocess.run(command, cwd=worktree, shell=True, text=True,
                                   capture_output=True, timeout=timeout)
        return RunResult(completed.returncode, completed.stdout, completed.stderr)
    except subprocess.TimeoutExpired as error:
        return RunResult(124, error.stdout or "", error.stderr or "", True)
