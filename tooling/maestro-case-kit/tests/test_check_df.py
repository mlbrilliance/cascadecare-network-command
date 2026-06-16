"""Tests for validate_df_entity (R6) — Data Fabric field-name traps."""

from __future__ import annotations

import json
from pathlib import Path

from maestro_case_kit import validators


def _write(p: Path, spec: dict) -> Path:
    p.write_text(json.dumps(spec), encoding="utf-8")
    return p


def test_clean_camelcase_spec_is_ok(tmp_path: Path) -> None:
    p = _write(tmp_path / "e.json", {"entity": "Provider", "fields": ["slug", "providerId", "displayName"]})
    assert validators.validate_df_entity(p) == []


def test_underscore_field_is_flagged_with_camelcase_suggestion(tmp_path: Path) -> None:
    p = _write(tmp_path / "e.json", {"entity": "Provider", "fields": ["provider_id"]})
    findings = validators.validate_df_entity(p)
    drop = [f for f in findings if f.rule_id == "DF-UNDERSCORE-DROP"]
    assert drop and "providerId" in drop[0].message


def test_reserved_id_is_flagged(tmp_path: Path) -> None:
    p = _write(tmp_path / "e.json", {"entity": "Provider", "fields": ["id"]})
    findings = validators.validate_df_entity(p)
    assert any(f.rule_id == "DF-RESERVED-ID" for f in findings)


def test_fields_as_objects_supported(tmp_path: Path) -> None:
    p = _write(tmp_path / "e.json", {"fields": [{"name": "bad_name"}, {"name": "goodName"}]})
    findings = validators.validate_df_entity(p)
    assert any(f.rule_id == "DF-UNDERSCORE-DROP" for f in findings)


def test_missing_spec_raises(tmp_path: Path) -> None:
    try:
        validators.validate_df_entity(tmp_path / "nope.json")
    except FileNotFoundError:
        return
    raise AssertionError("expected FileNotFoundError")
