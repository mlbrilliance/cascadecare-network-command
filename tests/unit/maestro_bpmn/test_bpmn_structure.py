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
    # The spawn callActivity bridges to the master case via the registry-canonical
    # releaseKey context field (bindingInfo.resource="process") bound to a process
    # binding — NOT a literal `name` input. The editor's "Process" selector reads
    # releaseKey; the literal-name form left it unresolved (the Studio Web error).
    bpmn_text = BPMN_FILES[0].read_text(encoding="utf-8")
    assert "StartCaseMgmtProcessAsync" in bpmn_text, (
        ".bpmn must spawn the master case via Orchestrator.StartCaseMgmtProcessAsync"
    )
    assert 'name="releaseKey"' in bpmn_text, (
        ".bpmn spawn call must wire the registry-canonical releaseKey context field"
    )
    assert "=bindings.Binding_MasterCrisisCase" in bpmn_text, (
        "releaseKey must be bound to the Binding_MasterCrisisCase process binding "
        "(must not regress to a literal name input)"
    )
    assert 'name="name" type="string" value="clearflow-master-crisis"' not in bpmn_text, (
        "the literal name context input must be gone — it left the editor's "
        "Process selector unresolved"
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


def test_cascade_gateway_reads_affected_customer_count() -> None:
    # The cascade decision lives in the gateway condition itself — it reads the
    # entry input `affectedCustomerCount` directly via `=vars.affectedCustomerCount`.
    # An earlier design computed an `isCascade` boolean in a JS scriptTask, but the
    # Studio Web editor never injected the variable into the script runtime
    # ("ReferenceError: affectedCustomerCount is not defined") and could not resolve
    # `=vars.isCascade`. Reading the count directly in the gateway removes the
    # scriptTask and the intermediate variable, so there is nothing left to mis-bind.
    bpmn_text = BPMN_FILES[0].read_text(encoding="utf-8")
    assert "=vars.affectedCustomerCount &gt;= 3" in bpmn_text, (
        "the cascade branch condition must read =vars.affectedCustomerCount >= 3"
    )
    assert "scriptTask" not in bpmn_text, (
        "the JS scriptTask was removed — its variables never registered in the editor"
    )
    assert "isCascade" not in bpmn_text, (
        "the intermediate isCascade variable was removed — the gateway reads the count directly"
    )
