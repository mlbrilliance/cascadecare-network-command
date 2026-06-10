"""
Slice 023.A — Targeted re-entry on the master case (clearflow-master-crisis).

Asserts the canonical Maestro Case "targeted re-entry" surface: at Reversal 5
(litigation / ClearFlow becomes co-defendant) the flow interrupts and re-opens the
prior Multi-Customer Investigation stage, re-running ONLY the selected task
(Multi-Customer Correlation) while the settled anomaly classification is skipped, then
returns to the originating stage via a `return-to-origin` exit.

This is the plan's "re-enter a prior stage, re-run ONLY selected tasks" pattern
(Pattern B): the re-entry attaches to the existing Stage_jsrEfr — no new node, no new
bindings. Guards the interrupting entry, the return-to-origin exit, and the per-task
shouldRunOnlyOnce split that together make the re-run targeted.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).parents[3]
MASTER = REPO_ROOT / "maestro_case" / "clearflow-master-crisis" / "caseplan.json"

REENTRY_STAGE_ID = "Stage_jsrEfr"  # Multi-Customer Investigation
GATING_VAR = "var_reversal_number"
SELECTED_TASK = "tMCPCor02"  # Multi-Customer Correlation — re-runs on re-entry
SETTLED_TASK = "tTNOuRcy1"  # Claim Flow Anomaly Detection — stays run-once


@pytest.fixture(scope="module")
def master() -> dict[str, Any]:
    return json.loads(MASTER.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def reentry_stage(master: dict[str, Any]) -> dict[str, Any]:
    for node in master["nodes"]:
        if node.get("id") == REENTRY_STAGE_ID:
            return node
    raise AssertionError(f"{REENTRY_STAGE_ID} not found in master caseplan")


def _all_rules(condition: dict[str, Any]) -> list[dict[str, Any]]:
    return [rule for clause in condition.get("rules", []) for rule in clause]


def test_master_caseplan_parses(master: dict[str, Any]) -> None:
    assert int(str(master["version"]).split(".")[0]) >= 20
    assert isinstance(master["nodes"], list)
    assert isinstance(master["edges"], list)


def test_interrupting_reentry_entry_condition(reentry_stage: dict[str, Any]) -> None:
    """An interrupting entry condition gated on the reversal var re-opens the stage."""
    entries = reentry_stage["data"]["entryConditions"]
    interrupting = [c for c in entries if c.get("isInterrupting") is True]
    assert len(interrupting) == 1, "expected exactly one interrupting re-entry condition"
    cond = interrupting[0]
    rules = _all_rules(cond)
    # Gated on case state via a =js: expression referencing the reversal var.
    gated = [
        r
        for r in rules
        if GATING_VAR in (r.get("conditionExpression") or "")
        and (r.get("conditionExpression") or "").startswith("=js:")
    ]
    assert gated, f"interrupting condition must gate on =js:vars.{GATING_VAR}"
    # The original (non-interrupting) "previous stage completed" entry survives.
    assert any(not c.get("isInterrupting") for c in entries), "lost original entry condition"


def test_return_to_origin_exit_condition(reentry_stage: dict[str, Any]) -> None:
    exits = reentry_stage["data"]["exitConditions"]
    rto = [c for c in exits if c.get("type") == "return-to-origin"]
    assert len(rto) == 1, "expected exactly one return-to-origin exit"
    assert rto[0].get("marksStageComplete") is True
    # The original exit-only completion path survives.
    assert any(c.get("type") != "return-to-origin" for c in exits), "lost original exit"


def test_selected_task_reruns_settled_task_does_not(reentry_stage: dict[str, Any]) -> None:
    tasks = {t["id"]: t for lane in reentry_stage["data"]["tasks"] for t in lane}
    assert tasks[SELECTED_TASK]["shouldRunOnlyOnce"] is False, (
        "selected task must re-run on re-entry"
    )
    assert tasks[SETTLED_TASK]["shouldRunOnlyOnce"] is True, (
        "settled anomaly task must stay run-once"
    )


def test_node_and_edge_counts_unchanged(master: dict[str, Any]) -> None:
    """Pattern B adds NO nodes and NO edges — re-entry is condition-driven."""
    stage_nodes = [n for n in master["nodes"] if n.get("type", "").endswith("Stage")]
    assert len(stage_nodes) == 7, "Pattern B must not add or remove stages"
    assert len(master["edges"]) == 7, "Pattern B must not add or remove edges"
