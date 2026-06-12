"""S025 gate: caseAppEnabled:true => metadata.caseAppConfig present and well-formed.

Covers the three canonical caseplans plus the idempotent ensure-step in the two
canvas merge scripts (the canvas may strip the key on round-trip; the merge
scripts must restore it without clobbering a canvas-authored config).
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

CASEPLANS = {
    "clearflow-master-crisis": REPO_ROOT
    / "maestro_case/clearflow-master-crisis/caseplan.json",
    "clearflow-stakeholder-parent": REPO_ROOT
    / "maestro_case/clearflow-stakeholder-parent/caseplan.json",
    "clearflow-obligation-grandchild": REPO_ROOT
    / "maestro_case/clearflow-obligation-grandchild/caseplan.json",
}


def _load_script(name: str):
    path = REPO_ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.replace("-", "_").removesuffix(".py"), path)
    assert spec is not None, f"cannot load {path}"
    assert spec.loader is not None, f"cannot load {path}"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _assert_well_formed(config: dict, case: str) -> None:
    assert isinstance(config.get("caseSummary"), str), f"{case}: caseSummary missing"
    assert config["caseSummary"].startswith("="), f"{case}: caseSummary must be an expression"
    sections = config.get("sections")
    assert isinstance(sections, list), f"{case}: sections missing"
    assert sections, f"{case}: sections empty"
    for s in sections:
        assert s.get("id", "").startswith("section-"), f"{case}: bad section id {s.get('id')}"
        assert s.get("title"), f"{case}: section missing title"
        details = json.loads(s["details"])  # JSON-encoded string per V20 contract
        assert isinstance(details, dict), f"{case}: details must be an object"
        assert details, f"{case}: details must be non-empty"
        for label, expr in details.items():
            assert isinstance(expr, str), f"{case}: section field {label!r} must be a string"
            assert expr.startswith("=vars."), (
                f"{case}: section field {label!r} must reference a case variable, got {expr!r}"
            )


class TestCanonicalCaseplans:
    def test_case_app_config_present_when_enabled(self) -> None:
        for case, path in CASEPLANS.items():
            d = json.loads(path.read_text())
            meta = d["metadata"]
            assert meta.get("caseAppEnabled") is True, f"{case}: caseAppEnabled flipped off"
            assert "caseAppConfig" in meta, f"{case}: caseAppEnabled without caseAppConfig"
            _assert_well_formed(meta["caseAppConfig"], case)

    def test_section_expressions_reference_declared_variables(self) -> None:
        for case, path in CASEPLANS.items():
            d = json.loads(path.read_text())
            declared = {
                v["id"]
                for bucket in d["variables"].values()
                for v in bucket
                if v.get("elementId") == "root"
            }
            config = d["metadata"]["caseAppConfig"]
            referenced = set()
            for s in config["sections"]:
                for expr in json.loads(s["details"]).values():
                    referenced.add(expr.removeprefix("=vars."))
            unknown = referenced - declared
            assert not unknown, f"{case}: caseAppConfig references undeclared variables {unknown}"


class TestMergeScriptEnsure:
    def _check_ensure(self, ensure, expected: dict) -> None:
        # missing -> added
        d = {"metadata": {"caseAppEnabled": True}}
        ensure(d)
        assert d["metadata"]["caseAppConfig"] == expected
        _assert_well_formed(d["metadata"]["caseAppConfig"], "ensure")
        # present (canvas-authored) -> untouched
        sentinel = {"caseSummary": "=vars.x", "sections": []}
        d2 = {"metadata": {"caseAppEnabled": True, "caseAppConfig": sentinel}}
        ensure(d2)
        assert d2["metadata"]["caseAppConfig"] is sentinel
        # disabled -> no-op
        d3 = {"metadata": {"caseAppEnabled": False}}
        ensure(d3)
        assert "caseAppConfig" not in d3["metadata"]

    def test_master_merge_script_restores_config(self) -> None:
        mod = _load_script("merge-canvas-download.py")
        self._check_ensure(mod.ensure_case_app_config, mod.CASE_APP_CONFIG)

    def test_child_grandchild_merge_script_restores_config(self) -> None:
        mod = _load_script("merge-child-grandchild.py")
        for case in ("clearflow-stakeholder-parent", "clearflow-obligation-grandchild"):
            expected = mod.CASE_APP_CONFIGS[case]

            def ensure(d: dict, _case: str = case) -> None:
                mod.ensure_case_app_config(d, _case)

            self._check_ensure(ensure, expected)

    def test_merge_constants_match_canonical_caseplans(self) -> None:
        master = _load_script("merge-canvas-download.py")
        child_gc = _load_script("merge-child-grandchild.py")
        expected_by_case = {
            "clearflow-master-crisis": master.CASE_APP_CONFIG,
            **child_gc.CASE_APP_CONFIGS,
        }
        for case, path in CASEPLANS.items():
            d = json.loads(path.read_text())
            assert d["metadata"]["caseAppConfig"] == expected_by_case[case], (
                f"{case}: canonical caseplan and merge-script constant drifted"
            )
