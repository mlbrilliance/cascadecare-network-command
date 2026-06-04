"""Slice 019/023 — BPMN→case bridge binding-resolution gate.

The BPMN `clearflow-ideal-incident-response` spawns the master crisis case via a
`StartCaseMgmtProcessAsync` call activity. As of Slice 023 the case is bound by
**inline `<uipath:binding>`** elements in the .bpmn (name + folderPath, the
editor-authored v2 contract — verified live 2026-06-04: the case spawned and
ran). Each binding's `resourceKey` must match a process **resource name** the
packed solution actually declares (`resources/solution_folder/process/**/*.json`
→ `resource.name`).

A binding whose `resourceKey` matches no solution resource is a *dangling*
binding: it packs and publishes fine, then silently fails to spawn at runtime
(or throws `170005 folderId missing` when the folder identity is absent). This
gate kills that whole class of bug.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
BPMN_DIR = REPO_ROOT / "maestro_bpmn" / "clearflow-ideal-incident-response"
BPMN_FILE = next(BPMN_DIR.glob("*.bpmn"))
SOLUTION_PROCESS_DIR = (
    REPO_ROOT
    / "maestro_case"
    / "clearflow-solution"
    / "resources"
    / "solution_folder"
    / "process"
)
BPMN_REGISTRATION = (
    SOLUTION_PROCESS_DIR
    / "processOrchestration"
    / "ClearFlowIdealIncidentResponse.json"
)


def _solution_process_resource_names() -> set[str]:
    """Every process `resource.name` the packed solution declares.

    These are the only keys a cross-project binding can resolve to.
    """
    names: set[str] = set()
    for manifest in SOLUTION_PROCESS_DIR.rglob("*.json"):
        data = json.loads(manifest.read_text(encoding="utf-8"))
        name = data.get("resource", {}).get("name")
        if name:
            names.add(name)
    return names


def _bpmn_inline_binding_keys() -> list[str]:
    """`resourceKey` of every inline <uipath:binding> in the .bpmn."""
    text = BPMN_FILE.read_text(encoding="utf-8")
    return re.findall(r'<uipath:binding\b[^>]*\bresourceKey="([^"]+)"', text)


def _registration_binding_types() -> list[str]:
    data = json.loads(BPMN_REGISTRATION.read_text(encoding="utf-8"))
    deps = data.get("resource", {}).get("runtimeDependencies", [])
    return [d.get("bindingType") for d in deps if d.get("bindingType")]


def test_solution_declares_the_master_case_resource() -> None:
    names = _solution_process_resource_names()
    assert "clearflow-master-crisis" in names, (
        "the packed solution must declare a process resource named "
        f"'clearflow-master-crisis'; found {sorted(names)}"
    )


def test_bpmn_has_inline_case_bindings() -> None:
    keys = _bpmn_inline_binding_keys()
    assert keys, (
        "the BPMN must declare inline <uipath:binding> elements for the spawn "
        "(name + folderPath) — the case is no longer bound via bindings_v2.json"
    )


@pytest.mark.parametrize("resource_key", sorted(set(_bpmn_inline_binding_keys())))
def test_inline_binding_resolves_to_a_real_resource(resource_key: str) -> None:
    """Every inline binding `resourceKey` must name a solution process resource."""
    names = _solution_process_resource_names()
    resolved = resource_key.lstrip(".")
    assert resolved in names, (
        f"BPMN inline binding resourceKey={resource_key!r} resolves to no solution "
        f"process resource (dangling binding). Available: {sorted(names)}"
    )


def test_registration_has_no_dangling_runtime_dependency() -> None:
    """Any registration `runtimeDependencies[].bindingType` must resolve.

    Inline bindings make an empty runtimeDependencies list valid; this gate only
    fails if a *non-resolving* dependency is (re)introduced.
    """
    names = _solution_process_resource_names()
    for bt in _registration_binding_types():
        assert bt.lstrip(".") in names, (
            f"solution registration bindingType={bt!r} resolves to no process "
            f"resource (deploy-time dangling binding). Available: {sorted(names)}"
        )
