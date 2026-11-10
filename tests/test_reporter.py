import json
from arena.reporter import write_reports


def test_writes_openable_reports(tmp_path):
    template = tmp_path / "template.html"
    template.write_text("{{OVERLAPS}} {{TASK_ROWS}} {{REPORT_JSON}}", encoding="utf-8")
    report = {"tasks": [{"id": "one", "runner": {"exit_code": 0}, "test": {"exit_code": 0}, "changed_paths": [], "diff": ""}], "overlapping_paths": []}
    json_path, html_path = write_reports(report, tmp_path / "out", template)
    assert json.loads(json_path.read_text())["tasks"][0]["id"] == "one"
    assert "one" in html_path.read_text()
