"""Tests for the `maestro-case lint` CLI surface (R4, R7)."""

from __future__ import annotations

import json
from pathlib import Path

from maestro_case_kit import cli

CLEAN = {
    "name": "demo",
    "stages": [{"id": "s1", "tasks": [{"id": "t1", "inputs": {"a": "=vars.x"}, "outputs": []}]}],
}
BPMN_NO_START = '<bpmn:process><bpmn:task id="t1" /></bpmn:process>'


def _mkcaseplan(d: Path, caseplan: dict, bpmn: str) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    (d / "caseplan.json").write_text(json.dumps(caseplan), encoding="utf-8")
    bp = d / "caseplan.json.bpmn"
    bp.write_text(bpmn, encoding="utf-8")
    import os

    os.utime(d / "caseplan.json", (1000, 1000))
    os.utime(bp, (2000, 2000))
    return d


def test_lint_clean_exits_zero(tmp_path: Path, capsys) -> None:
    d = _mkcaseplan(tmp_path / "c", CLEAN, '<bpmn:process><bpmn:startEvent id="s" /></bpmn:process>')
    rc = cli.main(["lint", str(d)])
    assert rc == 0


def test_lint_findings_exit_nonzero(tmp_path: Path, capsys) -> None:
    d = _mkcaseplan(tmp_path / "c", CLEAN, BPMN_NO_START)
    rc = cli.main(["lint", str(d)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "MC-NO-START-EVENT" in out


def test_lint_json_is_valid(tmp_path: Path, capsys) -> None:
    d = _mkcaseplan(tmp_path / "c", CLEAN, BPMN_NO_START)
    rc = cli.main(["lint", str(d), "--json"])
    out = capsys.readouterr().out
    assert rc == 1
    payload = json.loads(out)
    assert isinstance(payload, list) and payload
    assert {"rule_id", "severity", "message"} <= set(payload[0].keys())
