"""Tests for validate_caseplan static linting (R4, R7). Synthetic fixtures only."""

from __future__ import annotations

import json
import os
from pathlib import Path

from maestro_case_kit import validators

CLEAN_CASEPLAN = {
    "name": "demo-case",
    "stages": [
        {
            "id": "s1",
            "tasks": [
                {
                    "id": "t1",
                    "type": "agent",
                    "inputs": {"who": "=vars.stakeholder", "ctx": "=metadata.caseId"},
                    "outputs": [{"name": "Result", "var": "result"}],
                }
            ],
        }
    ],
}

BPMN_WITH_START = (
    '<bpmn:process><bpmn:startEvent id="se1"><bpmn:messageEventDefinition />'
    "</bpmn:startEvent><bpmn:task id=\"t1\" /></bpmn:process>"
)
BPMN_NO_START = '<bpmn:process><bpmn:task id="t1" /></bpmn:process>'


def _write_caseplan(d: Path, caseplan: dict, bpmn: str | None = BPMN_WITH_START) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    cp = d / "caseplan.json"
    cp.write_text(json.dumps(caseplan), encoding="utf-8")
    if bpmn is not None:
        bp = d / "caseplan.json.bpmn"
        bp.write_text(bpmn, encoding="utf-8")
        # Make .bpmn newer than caseplan.json (fresh/compiled state).
        os.utime(cp, (1000, 1000))
        os.utime(bp, (2000, 2000))
    return d


def _rule_ids(findings) -> set[str]:
    return {f.rule_id for f in findings}


def test_clean_caseplan_has_no_findings(tmp_path: Path) -> None:
    d = _write_caseplan(tmp_path / "c", CLEAN_CASEPLAN)
    findings = validators.lint_caseplan(d)
    assert findings == []


def test_missing_caseplan_raises(tmp_path: Path) -> None:
    try:
        validators.lint_caseplan(tmp_path / "nope")
    except FileNotFoundError:
        return
    raise AssertionError("expected FileNotFoundError for missing caseplan.json")


def test_stale_bpmn_is_flagged(tmp_path: Path) -> None:
    d = _write_caseplan(tmp_path / "c", CLEAN_CASEPLAN)
    # caseplan.json edited AFTER the .bpmn was compiled -> stale.
    os.utime(d / "caseplan.json", (3000, 3000))
    findings = validators.lint_caseplan(d)
    assert "MC-BPMN-STALE" in _rule_ids(findings)


def test_missing_start_event_is_flagged(tmp_path: Path) -> None:
    d = _write_caseplan(tmp_path / "c", CLEAN_CASEPLAN, bpmn=BPMN_NO_START)
    findings = validators.lint_caseplan(d)
    assert "MC-NO-START-EVENT" in _rule_ids(findings)


def test_missing_bpmn_is_a_warning(tmp_path: Path) -> None:
    d = _write_caseplan(tmp_path / "c", CLEAN_CASEPLAN, bpmn=None)
    findings = validators.lint_caseplan(d)
    assert "MC-NO-BPMN" in _rule_ids(findings)


def test_duplicate_output_var_is_flagged(tmp_path: Path) -> None:
    cp = json.loads(json.dumps(CLEAN_CASEPLAN))
    cp["stages"][0]["tasks"][0]["outputs"].append({"name": "Error", "var": "error"})
    cp["stages"][0]["tasks"][0]["outputs"].append({"name": "Error2", "var": "error"})
    d = _write_caseplan(tmp_path / "c", cp)
    findings = validators.lint_caseplan(d)
    assert "MC-DUP-OUTPUT-VAR" in _rule_ids(findings)


def test_legacy_dollar_expression_is_flagged(tmp_path: Path) -> None:
    cp = json.loads(json.dumps(CLEAN_CASEPLAN))
    cp["stages"][0]["tasks"][0]["inputs"]["who"] = "$vars.stakeholder"
    d = _write_caseplan(tmp_path / "c", cp)
    findings = validators.lint_caseplan(d)
    assert "MC-LEGACY-EXPR" in _rule_ids(findings)


def test_bad_expression_prefix_is_flagged(tmp_path: Path) -> None:
    cp = json.loads(json.dumps(CLEAN_CASEPLAN))
    cp["stages"][0]["tasks"][0]["inputs"]["who"] = "=qem.Provider[1]"
    d = _write_caseplan(tmp_path / "c", cp)
    findings = validators.lint_caseplan(d)
    assert "MC-BAD-EXPR-PREFIX" in _rule_ids(findings)


def test_jsonstring_prefix_is_allowed(tmp_path: Path) -> None:
    # =jsonString is a real V20 prefix used in live caseplans (regression guard).
    cp = json.loads(json.dumps(CLEAN_CASEPLAN))
    cp["stages"][0]["tasks"][0]["inputs"]["cfg"] = '=jsonString:{"a":1}'
    d = _write_caseplan(tmp_path / "c", cp)
    assert "MC-BAD-EXPR-PREFIX" not in _rule_ids(validators.lint_caseplan(d))


def test_output_source_target_bindings_are_not_flagged(tmp_path: Path) -> None:
    # outputs[].source/.target hold =FieldName bindings, not value expressions.
    cp = json.loads(json.dumps(CLEAN_CASEPLAN))
    cp["stages"][0]["tasks"][0]["outputs"] = [
        {"name": "Reviewer", "var": "reviewer", "source": "=ReviewerId", "target": "=reviewerId"}
    ]
    d = _write_caseplan(tmp_path / "c", cp)
    assert "MC-BAD-EXPR-PREFIX" not in _rule_ids(validators.lint_caseplan(d))


def test_findings_have_shape(tmp_path: Path) -> None:
    d = _write_caseplan(tmp_path / "c", CLEAN_CASEPLAN, bpmn=BPMN_NO_START)
    for f in validators.lint_caseplan(d):
        assert f.rule_id and f.severity in {"high", "medium", "low"}
        assert f.message
        assert isinstance(f.to_dict(), dict)
