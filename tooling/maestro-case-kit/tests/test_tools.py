"""Tests for the agent-native tool registry (shared by CLI and MCP)."""

from __future__ import annotations

import json
from pathlib import Path

from maestro_case_kit import tools


def test_registry_nonempty_and_unique() -> None:
    names = [t.name for t in tools.TOOLS]
    assert len(names) >= 4
    assert len(names) == len(set(names))


def test_every_tool_has_object_schema() -> None:
    for t in tools.TOOLS:
        assert t.description
        assert t.input_schema.get("type") == "object"
        assert "properties" in t.input_schema


def test_run_explain_returns_entry_dicts() -> None:
    result = tools.run_tool("maestro_case_explain", {"query": "400300"})
    assert isinstance(result, list) and result
    assert any(r["id"] == "MC-SPAWN-QEM-400300" for r in result)


def test_run_lint_on_fixture(tmp_path: Path) -> None:
    d = tmp_path / "c"
    d.mkdir()
    (d / "caseplan.json").write_text(json.dumps({"name": "x", "stages": []}), encoding="utf-8")
    (d / "caseplan.json.bpmn").write_text("<bpmn:process />", encoding="utf-8")
    result = tools.run_tool("maestro_case_lint", {"caseplan_dir": str(d)})
    assert isinstance(result, list)
    assert any(r["rule_id"] == "MC-NO-START-EVENT" for r in result)


def test_unknown_tool_raises() -> None:
    try:
        tools.run_tool("no_such_tool", {})
    except KeyError:
        return
    raise AssertionError("expected KeyError for unknown tool")
