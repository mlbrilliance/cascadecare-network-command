"""Tests for check_spawn_fanout (R5) — flags =datafabric.qem in spawn inputs."""

from __future__ import annotations

import json
from pathlib import Path

from maestro_case_kit import validators

BASE = {
    "name": "demo",
    "nodes": [
        {
            "id": "spawn1",
            "type": "spawn",
            "data": {"inputs": {"StakeholderId": "gamma", "MasterCaseId": "=metadata.caseId"}},
        }
    ],
}


def _write(d: Path, caseplan: dict) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    (d / "caseplan.json").write_text(json.dumps(caseplan), encoding="utf-8")
    return d


def test_literal_slug_spawn_is_clean(tmp_path: Path) -> None:
    d = _write(tmp_path / "c", BASE)
    assert validators.check_spawn_fanout(d) == []


def test_qem_in_spawn_input_is_flagged(tmp_path: Path) -> None:
    cp = json.loads(json.dumps(BASE))
    cp["nodes"][0]["data"]["inputs"]["StakeholderId"] = "=datafabric.qem:Provider[?(@.idx==1)].slug"
    d = _write(tmp_path / "c", cp)
    findings = validators.check_spawn_fanout(d)
    assert any(f.rule_id == "MC-SPAWN-QEM-400300" for f in findings)
    assert all(f.severity == "high" for f in findings if f.rule_id == "MC-SPAWN-QEM-400300")


def test_missing_caseplan_raises(tmp_path: Path) -> None:
    try:
        validators.check_spawn_fanout(tmp_path / "nope")
    except FileNotFoundError:
        return
    raise AssertionError("expected FileNotFoundError")
