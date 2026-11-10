from arena.evaluator import overlapping_paths


def test_finds_shared_changed_path():
    results = [{"changed_paths": ["a.py", "same.py"]}, {"changed_paths": ["same.py", "b.py"]}]
    assert overlapping_paths(results) == ["same.py"]
