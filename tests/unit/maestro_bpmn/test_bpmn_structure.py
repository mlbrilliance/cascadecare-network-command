"""Structural gate for the Slice 011 Maestro BPMN ideal-response model.

Offline check: the .bpmn is well-formed BPMN 2.0, walks intake → triage →
contain → notify → close, has the is_cascade gateway, and the cascade branch
bridges to the master crisis case. (`uip maestro bpmn validate` runs at deploy.)
"""

from __future__ import annotations

from pathlib import Path
from xml.dom import minidom

import re
import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
BPMN_DIR = REPO_ROOT / "maestro_bpmn" / "clearflow-ideal-incident-response"
BPMN_FILES = sorted(BPMN_DIR.glob("*.bpmn"))


def test_exactly_one_bpmn_source() -> None:
    assert len(BPMN_FILES) == 1, f"expected one .bpmn in {BPMN_DIR}, found {[p.name for p in BPMN_FILES]}"


def test_bpmn_is_well_formed_xml() -> None:
    minidom.parse(str(BPMN_FILES[0]))  # raises on malformed XML


@pytest.mark.parametrize("token", ["Triage", "Contain", "Notify", "Close", "Gateway_IsCascade", "SpawnMasterCrisis"])
def test_bpmn_contains_happy_path_and_cascade(token: str) -> None:
    text = BPMN_FILES[0].read_text(encoding="utf-8")
    assert token in text, f"BPMN model missing expected element/token {token!r}"


def test_one_start_and_one_end_event() -> None:
    doc = minidom.parse(str(BPMN_FILES[0]))
    starts = doc.getElementsByTagName("bpmn:startEvent") or doc.getElementsByTagName("startEvent")
    ends = doc.getElementsByTagName("bpmn:endEvent") or doc.getElementsByTagName("endEvent")
    assert len(starts) == 1, f"expected exactly one start event, got {len(starts)}"
    assert len(ends) == 1, f"expected exactly one end event, got {len(ends)}"


def test_cascade_branch_bridges_to_master_case() -> None:
    # The spawn callActivity bridges to the master case via the editor-authored
    # v2 contract (verified live 2026-06-04: the case spawned + ran). It binds the
    # case process by `name` + `folderPath` inline `<uipath:binding>` (the folder
    # identity is what the single `releaseKey` form lacked → runtime 170005
    # "folderId missing"). The CLI packer is the authority for this contract.
    bpmn_text = BPMN_FILES[0].read_text(encoding="utf-8")
    assert "StartCaseMgmtProcessAsync" in bpmn_text, (
        ".bpmn must spawn the master case via Orchestrator.StartCaseMgmtProcessAsync"
    )
    assert 'value="v2"' in bpmn_text or 'version="v2"' in bpmn_text, (
        "spawn activity must use the v2 StartCaseMgmtProcessAsync contract"
    )
    assert 'name="folderPath"' in bpmn_text, (
        "spawn must wire the folderPath context input (the folder identity that "
        "the releaseKey-only form lacked → runtime 170005 folderId missing)"
    )
    assert 'name="name"' in bpmn_text, (
        "spawn must wire the case process `name` context input"
    )
    assert 'propertyAttribute="folderPath"' in bpmn_text and 'propertyAttribute="name"' in bpmn_text, (
        "the inline <uipath:binding> pair (name + folderPath) must be present"
    )
    assert 'resourceKey="clearflow-master-crisis"' in bpmn_text, (
        "the spawn bindings must target the clearflow-master-crisis case resource"
    )


def test_spawn_satisfies_start_case_mgmt_contract() -> None:
    # SolutionPackager enforces the full Orchestrator.StartCaseMgmtProcessAsync
    # contract: a required JobArguments input payload AND an output payload.
    # Stripping either (done earlier to dodge an editor duplicate-output bug)
    # makes `uip solution pack` fail. The canonical output is a SINGLE line
    # (type Orchestrator.RunJob, no source) — the editor multiplies it per-field
    # only on manual delete+save, never from this source form.
    bpmn_text = BPMN_FILES[0].read_text(encoding="utf-8")
    assert 'name="JobArguments" type="json" target="bodyField"' in bpmn_text, (
        "spawn must pass a JobArguments json bodyField payload (packer-required)"
    )
    assert '<uipath:output name="Process response" type="Orchestrator.RunJob"' in bpmn_text, (
        "spawn must declare the canonical single Process response output"
    )
    # JobArguments keys must match the master case's declared variable names.
    for key in ("CaseGoal", "ReversalNumber", "ClearFlowVectorStatus", "GrandchildCaseCount", "SimulatedDay"):
        assert f'"{key}"' in bpmn_text, f"JobArguments must seed master-case variable {key!r}"


def test_vars_expressions_reference_declared_variable_names() -> None:
    # The Studio Web editor resolves `=vars.<token>` by the variable's NAME
    # (not its XML id) — referencing `=vars.Var_IsCascade` makes it report
    # "Variable 'vars.Var_IsCascade' does not exist", while `=vars.isCascade`
    # resolves. So every `=vars.<token>` must reference a declared variable NAME.
    # (The `var=`/`id=` structural attributes still use the id — those aren't
    # `=vars.` expressions and aren't checked here.)
    bpmn_text = BPMN_FILES[0].read_text(encoding="utf-8")
    declared_names = set(re.findall(r'<uipath:(?:input|inputOutput|output)\b[^>]*\bname="([^"]+)"', bpmn_text))
    assert declared_names, "no uipath variable declarations found"
    refs = set(re.findall(r"=vars\.([A-Za-z_][A-Za-z0-9_]*)", bpmn_text))
    unresolved = sorted(r for r in refs if r not in declared_names)
    assert not unresolved, (
        f"=vars.<token> must reference a declared variable NAME (editor resolves by name); "
        f"unresolved: {unresolved}; declared names: {sorted(declared_names)}"
    )


def test_cascade_gateway_reads_is_cascade() -> None:
    # The cascade decision reads the entry input `isCascade` directly via the
    # gateway condition `=vars.isCascade == true` (verified live 2026-06-04: the
    # gateway took the cascade branch with isCascade=true). `isCascade` is a
    # declared `inputOutput` entry variable — NOT a JS-scriptTask computed value
    # (that earlier approach never registered in the editor). No scriptTask exists,
    # so there is nothing to mis-bind; the caller passes the boolean at trigger.
    bpmn_text = BPMN_FILES[0].read_text(encoding="utf-8")
    assert "=vars.isCascade == true" in bpmn_text, (
        "the cascade branch condition must read =vars.isCascade == true"
    )
    assert "scriptTask" not in bpmn_text, (
        "no JS scriptTask — isCascade is a declared entry inputOutput, not computed"
    )
    assert '<uipath:inputOutput id="isCascade" name="isCascade" type="boolean"' in bpmn_text, (
        "isCascade must be a declared boolean entry inputOutput variable"
    )
