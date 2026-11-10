from __future__ import annotations

import html
import json
from pathlib import Path


def write_reports(report: dict, output_dir: Path, template: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "report.json"
    html_path = output_dir / "report.html"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    rows = "".join(
        "<section><h2>{}</h2><p>Runner: {} | Test: {}</p><h3>Changed paths</h3><pre>{}</pre>"
        "<h3>Diff</h3><pre>{}</pre></section>".format(
            html.escape(item["id"]), item["runner"]["exit_code"], item["test"]["exit_code"],
            html.escape("\n".join(item["changed_paths"]) or "(none)"), html.escape(item["diff"]))
        for item in report["tasks"])
    page = template.read_text(encoding="utf-8").replace("{{REPORT_JSON}}", html.escape(json.dumps(report)))
    page = page.replace("{{TASK_ROWS}}", rows).replace("{{OVERLAPS}}", html.escape(", ".join(report["overlapping_paths"]) or "None"))
    html_path.write_text(page, encoding="utf-8")
    return json_path, html_path
