"""Tests for the contribution gate — schema + IP-safety validation (R11)."""

from __future__ import annotations

import json
from pathlib import Path

from maestro_case_kit import contribution, knowledge

VALID = {
    "id": "MC-EXAMPLE",
    "kind": "runtime",
    "title": "Example footgun",
    "surface": "Maestro Case",
    "symptom": "Something surprising happens.",
    "error_signatures": ["999999"],
    "cause": "Because of a thing.",
    "fix": "Do the other thing.",
    "proven_on": "1.0.0",
    "severity": "medium",
    "references": ["docs/x.md"],
}


def test_valid_entry_has_no_problems() -> None:
    assert contribution.validate_entry(VALID) == []


def test_missing_field_is_a_problem() -> None:
    bad = {k: v for k, v in VALID.items() if k != "fix"}
    problems = contribution.validate_entry(bad)
    assert any("fix" in p for p in problems)


def test_bad_severity_is_a_problem() -> None:
    bad = {**VALID, "severity": "catastrophic"}
    assert any("severity" in p for p in contribution.validate_entry(bad))


def test_error_signatures_must_be_a_list() -> None:
    bad = {**VALID, "error_signatures": "999999"}
    assert any("error_signatures" in p for p in contribution.validate_entry(bad))


def test_denylist_token_is_flagged() -> None:
    bad = {**VALID, "cause": "This references ForbiddenCo internally."}
    problems = contribution.validate_entry(bad, denylist=["forbiddenco"])
    assert any("forbiddenco" in p.lower() for p in problems)


def test_validate_knowledge_detects_duplicate_ids() -> None:
    data = {"entries": [VALID, {**VALID}]}
    assert any("duplicate id" in p for p in contribution.validate_knowledge(data))


def test_bundled_seed_passes_the_gate() -> None:
    entries = [e.to_dict() for e in knowledge.load_entries()]
    assert contribution.validate_knowledge({"entries": entries}) == []


def test_validate_knowledge_accepts_a_path(tmp_path: Path) -> None:
    p = tmp_path / "k.json"
    p.write_text(json.dumps({"entries": [VALID]}), encoding="utf-8")
    assert contribution.validate_knowledge(p) == []
