"""Feature-presence tests for the Slice-014 platform wiring.

Slice 014 wired three brand-new UiPath Maestro features the judges will look
for (see CLAUDE.md "Platform features to integrate"). The generic V20
conformance suite (test_caseplan_structure.py) does not know about these
specific bindings, so this module guards them explicitly:

  1. ``qem:`` Data Fabric fan-out  — Reversal 3, master caseplan: six
     ``case-management`` spawn tasks, one per provider, each binding the
     provider via a ``=datafabric.qem:Provider[...]`` reference on the
     ``StakeholderId`` input.
  2. HITL reviewer-context capture — Reversal 4, master caseplan: the tri-party
     HITL gate is an ``action`` task that captures reviewer context into
     ``data.outputs[]`` for the post-HITL stage to read.
  3. SLA-breach notification — grandchild caseplan: targeted notification fires
     via a stage SLA escalation rule (``action.type == "notification"``).

These are deliberately tied to specific caseplans (not parametrized over all),
because they assert the narrative wiring, not generic schema shape.

Schema note: ``hitlTask`` and ``Maestro.NotificationService`` are NOT valid
Maestro Case V20 task ``type`` values — Studio Web's importer rejects any
caseplan containing them ("JSON is not a valid Case Management JSON of any
previous version"). The closed task-type enum is: process, action, agent,
api-workflow, rpa, external-agent, wait-for-timer, wait-for-connector,
execute-connector-activity, case-management. The HITL gate therefore uses
``action`` (the canonical human-approval task) and the SLA-breach notification
uses an SLA escalation rule (the schema-native notify-on-breach mechanism).
These tests assert the feature *intent* in its schema-valid form.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
MAESTRO_ROOT = REPO_ROOT / "maestro_case"

MASTER = MAESTRO_ROOT / "clearflow-master-crisis" / "content" / "caseplan.json"
GRANDCHILD = MAESTRO_ROOT / "clearflow-obligation-grandchild" / "content" / "caseplan.json"

# The six provider customers fanned out at Reversal 3 (CLAUDE.md naming table).
EXPECTED_PROVIDERS = {"northstar", "alpha", "beta", "gamma", "delta", "epsilon"}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _iter_tasks(caseplan: dict[str, Any]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """Yield (stage_node, task) pairs across the whole caseplan."""
    pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for node in caseplan.get("nodes", []):
        data = node.get("data", {})
        if not isinstance(data, dict):
            continue
        for entry in data.get("tasks", []):
            for task in entry if isinstance(entry, list) else [entry]:
                if isinstance(task, dict):
                    pairs.append((node, task))
    return pairs


def _tasks_of_type(caseplan: dict[str, Any], task_type: str) -> list[dict[str, Any]]:
    return [t for _, t in _iter_tasks(caseplan) if t.get("type") == task_type]


class TestQemFanOut:
    """Reversal 3 — the hero moment: six simultaneous qem: Provider spawns."""

    def test_six_case_management_spawns_in_one_stage(self) -> None:
        master = _load(MASTER)
        spawns = _tasks_of_type(master, "case-management")
        assert len(spawns) == 6, (
            f"Reversal-3 fan must be exactly 6 case-management spawns, got {len(spawns)}"
        )
        stages = {node.get("id") for node, t in _iter_tasks(master) if t.get("type") == "case-management"}
        assert len(stages) == 1, (
            f"All 6 spawns must share one stage for the visible fan, got stages {stages}"
        )

    @staticmethod
    def _stakeholder_ref(task: dict[str, Any]) -> str:
        """The qem:Provider binding lives on the StakeholderId input value.

        ``dataFabricEntityRef`` as a top-level task field is not part of the
        V20 BaseTask schema; the Data Fabric entity reference is carried by the
        ``StakeholderId`` input instead (the runtime binding that actually
        wires the provider entity into the spawned child case).
        """
        for inp in task.get("data", {}).get("inputs", []):
            if inp.get("name") == "StakeholderId":
                return str(inp.get("value", ""))
        return ""

    def test_every_spawn_has_qem_provider_entity_ref(self) -> None:
        master = _load(MASTER)
        offenders: list[str] = []
        for _, task in _iter_tasks(master):
            if task.get("type") != "case-management":
                continue
            ref = self._stakeholder_ref(task)
            if not ref.startswith("=datafabric.qem:Provider["):
                offenders.append(f"{task.get('id')} -> {ref!r}")
        assert not offenders, f"spawns missing qem:Provider entity ref: {offenders}"

    def test_no_spawn_carries_invalid_datafabric_entity_ref_field(self) -> None:
        """Guard against regressing to the Studio-Web-rejected top-level field."""
        master = _load(MASTER)
        offenders = [
            task.get("id")
            for _, task in _iter_tasks(master)
            if task.get("type") == "case-management" and "dataFabricEntityRef" in task
        ]
        assert not offenders, (
            "case-management tasks must not carry a top-level dataFabricEntityRef "
            f"(not a valid V20 BaseTask field); offenders: {offenders}"
        )

    def test_all_six_providers_covered(self) -> None:
        master = _load(MASTER)
        found: set[str] = set()
        for _, task in _iter_tasks(master):
            if task.get("type") != "case-management":
                continue
            ref = self._stakeholder_ref(task)
            for provider in EXPECTED_PROVIDERS:
                if f"slug='{provider}'" in ref:
                    found.add(provider)
        assert found == EXPECTED_PROVIDERS, (
            f"missing providers in Reversal-3 fan: {sorted(EXPECTED_PROVIDERS - found)}"
        )

    def test_spawn_inputs_bind_stakeholder_and_master_case(self) -> None:
        master = _load(MASTER)
        for _, task in _iter_tasks(master):
            if task.get("type") != "case-management":
                continue
            inputs = {i.get("name"): str(i.get("value", "")) for i in task.get("data", {}).get("inputs", [])}
            assert "StakeholderId" in inputs, f"{task.get('id')} missing StakeholderId input"
            assert inputs["StakeholderId"].startswith("=datafabric.qem:Provider["), (
                f"{task.get('id')} StakeholderId must resolve from Data Fabric, got {inputs['StakeholderId']!r}"
            )
            assert inputs.get("MasterCaseId") == "=metadata.caseId", (
                f"{task.get('id')} MasterCaseId must back-ref the master case"
            )


class TestHitlReviewerContext:
    """Reversal 4 — tri-party fiduciary HITL gate captures reviewer context.

    Expressed as an ``action`` task (the schema-valid human-approval type);
    reviewer context is captured into ``data.outputs[]`` for the post-HITL
    stage to read.
    """

    HITL_TITLE = "Tri-Party Fiduciary Conflict: Apex vs ClearFlow vs Provider BAAs"

    def _hitl_task(self) -> dict[str, Any]:
        actions = [
            t
            for t in _tasks_of_type(_load(MASTER), "action")
            if t.get("data", {}).get("taskTitle") == self.HITL_TITLE
        ]
        assert len(actions) == 1, (
            f"expected one HITL action task (Reversal 4), got {len(actions)}"
        )
        return actions[0]

    def test_master_has_exactly_one_hitl_task(self) -> None:
        self._hitl_task()  # asserts exactly one

    def test_hitl_uses_valid_action_type_not_hitltask(self) -> None:
        """Guard against regressing to the Studio-Web-rejected ``hitlTask`` type."""
        assert not _tasks_of_type(_load(MASTER), "hitlTask"), (
            "hitlTask is not a valid V20 task type — Studio Web rejects it; "
            "the HITL gate must use type 'action'"
        )

    def test_hitl_captures_reviewer_context_output(self) -> None:
        out_names = {o.get("name") for o in self._hitl_task().get("data", {}).get("outputs", [])}
        assert "ReviewerContext" in out_names, (
            f"HITL gate must capture ReviewerContext output, got {sorted(out_names)}"
        )
        assert "ReviewerDecision" in out_names, "HITL gate must capture ReviewerDecision"


class TestSlaBreachNotification:
    """Grandchild SLA-breach — schema-native notify-on-breach via SLA escalation.

    ``Maestro.NotificationService`` is not a valid task type; the targeted
    SLA-breach notification is expressed as an SLA escalation rule with
    ``action.type == "notification"`` on the Obligation Response stage.
    """

    @staticmethod
    def _escalations(caseplan: dict[str, Any]) -> list[dict[str, Any]]:
        escalations: list[dict[str, Any]] = []
        for node in caseplan.get("nodes", []):
            for rule in node.get("data", {}).get("slaRules", []):
                escalations.extend(rule.get("escalationRule", []))
        return escalations

    def test_grandchild_has_no_invalid_notification_task(self) -> None:
        """Guard against regressing to the Studio-Web-rejected task type."""
        assert not _tasks_of_type(_load(GRANDCHILD), "Maestro.NotificationService"), (
            "Maestro.NotificationService is not a valid V20 task type — "
            "Studio Web rejects it; use an SLA escalation notification instead"
        )

    def test_grandchild_has_sla_breach_notification(self) -> None:
        breach = [
            e
            for e in self._escalations(_load(GRANDCHILD))
            if e.get("triggerInfo", {}).get("type") == "sla-breached"
            and e.get("action", {}).get("type") == "notification"
        ]
        assert breach, (
            "grandchild caseplan must have an sla-breached notification escalation"
        )

    def test_notification_has_recipients_and_template(self) -> None:
        breach = next(
            e
            for e in self._escalations(_load(GRANDCHILD))
            if e.get("triggerInfo", {}).get("type") == "sla-breached"
        )
        action = breach.get("action", {})
        assert action.get("recipients"), "SLA-breach notification must declare recipients"
        assert action.get("messageTemplate"), (
            "SLA-breach notification must declare a messageTemplate"
        )
