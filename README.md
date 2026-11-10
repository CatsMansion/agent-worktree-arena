# Agent Worktree Arena

A deliberately small, local-first harness for comparing coding-agent tasks in isolated Git worktrees.

It creates one detached worktree per task, runs a runner and a task test there, records logs/exit codes/timeouts, compares changed paths, and writes a portable HTML and JSON report. It does not auto-merge, auto-push, or require an API key.

## Requirements

- Python 3.11+
- Git with an initial commit in the repository to evaluate

## Quick demo

From this project root:

```sh
python -m arena.cli --repo . --tasks examples/demo_tasks.json --output arena-report
```

The demo uses two deterministic offline runners. It produces independent `agent-a` and `agent-b` worktrees under `.arena/worktrees` while running, tests `arena_demo/alpha.txt` and `arena_demo/beta.txt` separately, then cleans those worktrees safely. Open `arena-report/report.html` in a browser.

Use `--keep-worktrees` to inspect them, then remove only Arena-created worktrees with:

```sh
python -m arena.cli --repo . --clean
```

## Real runners

Use a configured command template with `{prompt}` and `{task_id}` substitutions. The command is deliberately opt-in because it executes locally in each worktree.

```sh
python -m arena.cli --runner command --runner-command 'codex exec "{prompt}"' --tasks my_tasks.json
```

Each task JSON item needs `id`, `prompt`, and `test_command`; the demo runner additionally uses `expected_file` and `expected_content`.

## Development

```sh
python -m pip install -e '.[dev]'
pytest
```

GitHub Actions repeats these checks on Python 3.11. The generated reports are ignored by Git, and the project includes the MIT license.
