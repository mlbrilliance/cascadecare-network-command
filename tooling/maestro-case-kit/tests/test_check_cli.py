"""Tests for check_cli_namespace — guards the `uip maestro` CLI namespace footgun."""

from __future__ import annotations

from pathlib import Path

from maestro_case_kit import validators


def test_bare_uip_case_is_flagged(tmp_path: Path) -> None:
    f = tmp_path / "run.sh"
    f.write_text("uip case list --folder x\n", encoding="utf-8")
    findings = validators.check_cli_namespace(f)
    assert any(x.rule_id == "CLI-MAESTRO-NAMESPACE" for x in findings)
    assert any("uip maestro case" in x.message for x in findings)


def test_correct_namespace_is_not_flagged(tmp_path: Path) -> None:
    f = tmp_path / "run.sh"
    f.write_text("uip maestro case list\nuip maestro flow run\nuip maestro bpmn validate\n", encoding="utf-8")
    assert validators.check_cli_namespace(f) == []


def test_flow_and_bpmn_are_flagged(tmp_path: Path) -> None:
    f = tmp_path / "a.md"
    f.write_text("`uip flow run`\n`uip bpmn validate`\n", encoding="utf-8")
    findings = validators.check_cli_namespace(f)
    assert len(findings) == 2
    assert {x.rule_id for x in findings} == {"CLI-MAESTRO-NAMESPACE"}


def test_directory_scan_counts_only_bare(tmp_path: Path) -> None:
    (tmp_path / "a.sh").write_text("uip case get 1\n", encoding="utf-8")
    (tmp_path / "b.py").write_text("# uip flow list\n", encoding="utf-8")
    (tmp_path / "c.md").write_text("uip maestro case get 1\n", encoding="utf-8")  # clean
    findings = validators.check_cli_namespace(tmp_path)
    assert len(findings) == 2


def test_missing_path_raises(tmp_path: Path) -> None:
    try:
        validators.check_cli_namespace(tmp_path / "nope")
    except FileNotFoundError:
        return
    raise AssertionError("expected FileNotFoundError")
