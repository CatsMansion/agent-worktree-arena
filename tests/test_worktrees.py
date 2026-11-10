from pathlib import Path
from arena.worktrees import worktree_root


def test_worktree_root_is_scoped_to_arena(tmp_path):
    assert worktree_root(Path(tmp_path)) == tmp_path / ".arena" / "worktrees"
