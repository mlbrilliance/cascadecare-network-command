"""
Slice 021 — SLA + escalation -> Maestro Notification across all three case levels.

Asserts that the master and parent caseplans now carry case-level `metadata.slaRules`
and stage-level `slaRules` whose `escalationRule` entries fire `sla-breached` and
`at-risk` notification actions (the canonical Academy escalation pattern), mirroring the
shape already present in the grandchild caseplan. Guards against regressing the SLA
surfaces that drive the on-canvas at-risk/breached badge flips during the reversals.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).parents[3]
MAESTRO_ROOT = REPO_ROOT / "maestro_case"

CASEPLANS = {
    "master": MAESTRO_ROOT / "clearflow-master-crisis" / "caseplan.json",
    "parent": MAESTRO_ROOT / "clearflow-stakeholder-parent" / "caseplan.json",
    "grandchild": MAESTRO_ROOT / "clearflow-obligation-grandchild" / "caseplan.json",
}

# Master stages that must carry an SLA (terminal "Closed" excluded).
MASTER_SLA_STAGES = {
    "Initial Response",
    "Multi-Customer Investigation",
    "Vector Isolation",
    "Regulatory Response",
    "Fiduciary Review",
    "Litigation Defense",
}
PARENT_SLA_STAGES = {
    "Stakeholder Onboarding",
    "Impact Assessment",
    "Obligation Determination",
}


def _load(level: str) -> dict[str, Any]:
    path = CASEPLANS[level]
    assert path.exists(), f"{level} caseplan missing: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def _stage_nodes(doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for n in doc.get("nodes", []):
        if "Stage" in n.get("type", ""):
            data = n.get("data", {})
            label = data.get("label")
            if label:
                out[label] = data
    return out


def _escalation_triggers(sla_rules: list[dict[str, Any]]) -> set[str]:
    triggers: set[str] = set()
    for rule in sla_rules:
        for esc in rule.get("escalationRule", []):
            triggers.add(esc.get("triggerInfo", {}).get("type", ""))
    return triggers


def _notification_recipients(sla_rules: list[dict[str, Any]]) -> list[str]:
    targets: list[str] = []
    for rule in sla_rules:
        for esc in rule.get("escalationRule", []):
            action = esc.get("action", {})
            if action.get("type") == "notification":
                for r in action.get("recipients", []):
                    targets.append(r.get("target", ""))
    return targets


@pytest.mark.parametrize("level", ["master", "parent", "grandchild"])
def test_case_level_sla_rules_present(level: str) -> None:
    md = _load(level)["metadata"]
    rules = md.get("slaRules")
    assert rules, f"{level}: metadata.slaRules missing/empty"
    assert all("count" in r and "unit" in r for r in rules), f"{level}: malformed slaRules"


@pytest.mark.parametrize(
    "level,expected",
    [("master", MASTER_SLA_STAGES), ("parent", PARENT_SLA_STAGES)],
)
def test_stage_sla_with_notification_escalation(level: str, expected: set[str]) -> None:
    stages = _stage_nodes(_load(level))
    missing = []
    for label in expected:
        data = stages.get(label)
        if not data or not data.get("slaRules"):
            missing.append(f"{label}: no stage slaRules")
            continue
        triggers = _escalation_triggers(data["slaRules"])
        if "sla-breached" not in triggers:
            missing.append(f"{label}: no sla-breached escalation")
        if "at-risk" not in triggers:
            missing.append(f"{label}: no at-risk escalation")
        recips = _notification_recipients(data["slaRules"])
        if not any("caseOwner" in t for t in recips):
            missing.append(f"{label}: notification has no caseOwner recipient")
    assert not missing, f"{level} SLA/escalation gaps:\n" + "\n".join(missing)


def test_grandchild_sla_not_regressed() -> None:
    # Grandchild already had the pattern; ensure it still does (regression guard).
    stages = _stage_nodes(_load("grandchild"))
    assert any(d.get("slaRules") for d in stages.values()), "grandchild lost its stage SLA"
