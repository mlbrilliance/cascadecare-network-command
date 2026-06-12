"""Structural gate for Slice 006 Integration Service API Workflows.

Each external system gets one workflow at api_workflows/<slug>/main.json. The
slug must be a registered source_system, the file must be a valid CNCF
Serverless Workflow 1.0.0 doc (WorkflowStart first, strict JS, single root
Sequence), and every event-emitting workflow must carry its event_type const
and its own source_system slug so the payload matches the event contract.

Connector reads + Maestro Trigger emission are wired at deploy (uip offline),
so this checks STRUCTURE + the event/source mapping, not live execution.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
API_ROOT = REPO_ROOT / "api_workflows"
VOCAB_PATH = REPO_ROOT / "specs" / "003-uipath-native" / "case-vocabulary.yaml"

# slug -> event_type const(s) the workflow's payload must carry. None = utility (no Maestro event).
EXPECTED_EVENTS: dict[str, tuple[str, ...]] = {
    "provider-northstar": ("provider-claim-anomaly",),
    "provider-alpha": ("provider-claim-anomaly",),
    "provider-beta": ("provider-claim-anomaly",),
    "provider-gamma": ("provider-claim-anomaly",),
    "provider-delta": ("provider-claim-anomaly",),
    "provider-epsilon": ("provider-claim-anomaly",),
    "payer-apex": ("payer-demand",),
    "payer-summitblue": ("payer-demand",),
    "payer-union-prairie": ("payer-demand",),
    "payer-lakeshore": ("payer-demand",),
    "vendor-nimbus": ("vendor-attribution",),
    "regulator-tn-doi": ("regulatory-subpoena", "litigation-event"),
    "insurer-aurora-specialty": ("insurer-directive",),
    "counsel-hawthorne": (),  # utility workflow — no Maestro event
    "generate-audit-record": (),  # utility workflow — audit logging
    "register-stakeholder": (),  # utility workflow — stakeholder registration
    # Healthcare Agentic Solutions (S024) — case-invoked api-workflow tasks (referenced by the
    # stakeholder-parent caseplan's ApiWorkflow binding), NOT event-emitting source-system mocks.
    "solution-medical-records-summarization": (),
    "solution-claim-denial-prevention": (),
    "solution-prior-auth-continuity": (),
}

# Case-invoked Healthcare-solution workflows + utility workflows — exempt from the source-system/event contract.
SOLUTION_SLUGS = {
    "solution-medical-records-summarization",
    "solution-claim-denial-prevention",
    "solution-prior-auth-continuity",
    "counsel-hawthorne",
    "generate-audit-record",
    "register-stakeholder",
}

WORKFLOWS = sorted(API_ROOT.glob("*/main.json"))
PARAMS = [pytest.param(p, id=p.parent.name) for p in WORKFLOWS]


def _vocab_source_systems() -> set[str]:
    return set(yaml.safe_load(VOCAB_PATH.read_text()).get("source_systems", []))


def test_all_workflows_present() -> None:
    found = {p.parent.name for p in WORKFLOWS}
    assert found == set(EXPECTED_EVENTS), (
        f"api_workflows mismatch.\n  missing: {sorted(set(EXPECTED_EVENTS) - found)}"
        f"\n  unexpected: {sorted(found - set(EXPECTED_EVENTS))}"
    )


def test_every_source_system_slug_is_registered() -> None:
    # Source-system mocks must be registered; case-invoked Healthcare solutions are exempt.
    src = _vocab_source_systems()
    offenders = {p.parent.name for p in WORKFLOWS} - src - SOLUTION_SLUGS
    assert not offenders, f"workflow slugs not in vocabulary.source_systems: {sorted(offenders)}"


@pytest.mark.parametrize("path", PARAMS)
class TestWorkflowFile:
    def test_valid_serverless_workflow_doc(self, path: Path) -> None:
        wf = json.loads(path.read_text(encoding="utf-8"))
        assert wf.get("document", {}).get("dsl") == "1.0.0", f"{path}: document.dsl must be 1.0.0"
        ev = wf.get("evaluate", {})
        assert ev.get("language") == "javascript", f"{path}: evaluate.language must be javascript"
        assert ev.get("mode") == "strict", f"{path}: evaluate.mode must be strict"
        do = wf.get("do")
        assert isinstance(do, list), f"{path}: root 'do' must be a list"
        assert len(do) == 1, f"{path}: root 'do' must hold exactly one sequence"

    def test_workflowstart_is_first_activity(self, path: Path) -> None:
        wf = json.loads(path.read_text(encoding="utf-8"))
        root_seq = next(iter(wf["do"][0].values()))  # the single root Sequence body
        first_activity_key = next(iter(root_seq["do"][0]))
        assert first_activity_key == "WorkflowStart", (
            f"{path}: first activity must be WorkflowStart, got {first_activity_key!r}"
        )

    def test_has_terminating_response(self, path: Path) -> None:
        text = path.read_text(encoding="utf-8")
        assert '"then": "end"' in text or '"then":"end"' in text, (
            f"{path}: must contain a Response with then:'end'"
        )

    def test_emits_expected_event_and_own_slug(self, path: Path) -> None:
        slug = path.parent.name
        text = path.read_text(encoding="utf-8")
        for event_type in EXPECTED_EVENTS[slug]:
            assert event_type in text, f"{path}: expected event_type {event_type!r} not found"
        if EXPECTED_EVENTS[slug]:  # event-emitting workflows carry their source_system slug
            assert slug in text, f"{path}: source_system slug {slug!r} not present in payload"
