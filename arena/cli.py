from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .evaluator import changes, overlapping_paths, test_task
from .reporter import write_reports
from .runners import command_runner, demo_runner
from .worktrees import WorktreeError, clean_all, create


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run tasks in isolated Git worktrees.")
    p.add_argument("--repo", type=Path, default=Path.cwd())
    p.add_argument("--tasks", type=Path, default=Path("examples/demo_tasks.json"))
    p.add_argument("--runner", choices=("demo", "command"), default="demo")
    p.add_argument("--runner-command", help="Command template: use {prompt} and {task_id}.")
    p.add_argument("--timeout", type=int, default=60)
    p.add_argument("--output", type=Path, default=Path("arena-report"))
    p.add_argument("--clean", action="store_true")
    p.add_argument("--keep-worktrees", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    repo = args.repo.resolve()
    if args.clean:
        try:
            clean_all(repo); print("Cleaned .arena/worktrees"); return 0
        except WorktreeError as error:
            print(f"arena: {error}", file=sys.stderr); return 2
    if args.runner == "command" and not args.runner_command:
        print("arena: --runner-command is required for command runner", file=sys.stderr); return 2
    task_file = args.tasks if args.tasks.is_absolute() else repo / args.tasks
    tasks = json.loads(task_file.read_text(encoding="utf-8"))["tasks"]
    results: list[dict] = []
    try:
        for task in tasks:
            tree = create(repo, task["id"])
            runner = demo_runner(tree, task, args.timeout) if args.runner == "demo" else command_runner(tree, task, args.runner_command, args.timeout)
            test = test_task(tree, task["test_command"], args.timeout)
            changed_paths, diff = changes(tree)
            results.append({"id": task["id"], "prompt": task["prompt"], "worktree": str(tree), "runner": runner.__dict__, "test": test, "changed_paths": changed_paths, "diff": diff})
        report = {"generated_at": datetime.now(timezone.utc).isoformat(), "repo": str(repo), "runner": args.runner, "tasks": results, "overlapping_paths": overlapping_paths(results)}
        out = args.output if args.output.is_absolute() else repo / args.output
        json_path, html_path = write_reports(report, out, repo / "templates" / "report.html")
        print(f"JSON report: {json_path}"); print(f"HTML report: {html_path}")
        print("Overlaps:", ", ".join(report["overlapping_paths"]) or "none")
        return 0 if all(x["runner"]["exit_code"] == 0 and x["test"]["exit_code"] == 0 for x in results) else 1
    except (WorktreeError, KeyError, OSError, json.JSONDecodeError) as error:
        print(f"arena: {error}", file=sys.stderr); return 2
    finally:
        if not args.keep_worktrees:
            try: clean_all(repo)
            except WorktreeError: pass


if __name__ == "__main__":
    raise SystemExit(main())
