"""Dashboard business logic for ClearFlow Network Command.

build_payload() is the single entry point for GET /dashboard.

Offline mode (default): returns a fixture for the Day-30 demo narrative.
Live mode (UIPATH_LIVE=true or live=True kwarg): reads from UiPath Data Fabric
via the uipath SDK (EntitiesService).  Requires env vars:
  UIPATH_CLIENT_ID, UIPATH_CLIENT_SECRET, UIPATH_BASE_URL
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from models import (
    AgentActivity,
    AgentStatus,
    AgentType,
    CascadeTree,
    CaseNode,
    CaseStatus,
    DashboardPayload,
    OverrideAction,
    OverrideControl,
    ReversalEvent,
)

# ---------------------------------------------------------------------------
# Static data tables — add a row here to extend; no constructor blocks needed
# ---------------------------------------------------------------------------

_MASTER_ID = "case-master-cfcs"

# (slug, display_name, stage)
_PARENTS: list[tuple[str, str, str]] = [
    ("northstar", "Northstar Regional Health", "Contain"),
    ("alpha",     "Provider Alpha",             "Contain"),
    ("beta",      "Provider Beta",              "Contain"),
    ("gamma",     "Provider Gamma",             "Contain"),
    ("delta",     "Provider Delta",             "Contain"),
    ("epsilon",   "Provider Epsilon",           "Contain"),
    ("apex",      "Apex Health Plan",           "Notify"),
    ("summitblue","SummitBlue Medicare Advantage","Notify"),
    ("nimbus",    "Nimbus Patient Engagement Platform","Investigate"),
]

# Provider slugs that get TN-DOI grandchild cases at Reversal 3 (first 6)
_PROVIDER_SLUGS = [slug for slug, _, _ in _PARENTS[:6]]

# (number, name, day, wall_clock_s, goal_from, goal_to)
_REVERSALS: list[tuple[int, str, int, int, str, str]] = [
    (1, "Multi-customer correlation",       1,  10,
     "Assist isolated customers",
     "Determine if ClearFlow is the vector"),
    (2, "ClearFlow cleared, Nimbus identified", 5, 25,
     "Determine if ClearFlow is the vector",
     "Bystander posture: strategic decision required"),
    (3, "State DOI subpoena collision",    30,  45,
     "Bystander posture: strategic decision required",
     "Three-level nesting active: 6 grandchild obligation cases open"),
    (4, "Payer demands vs BAAs",           45,  75,
     "Three-level nesting active: regulatory response in progress",
     "Fiduciary conflict: tri-party HITL gate required"),
    (5, "Litigation cascade",              90, 120,
     "Fiduciary conflict resolution in progress",
     "Bystander becomes co-defendant: privilege reshuffles"),
]

# (agent_id, display_name, agent_type)
_AGENTS: list[tuple[str, str, AgentType]] = [
    ("claim-flow-anomaly-detector",    "Claim Flow Anomaly Detector",    AgentType.coded),
    ("multi-customer-pattern-detector","Multi-Customer Pattern Detector", AgentType.coded),
    ("forensic-self-exam-agent",       "Forensic Self-Exam Agent",        AgentType.coded),
    ("vector-hypothesis-agent",        "Vector Hypothesis Agent",         AgentType.builder),
    ("baa-boundary-reasoner",          "BAA Boundary Reasoner",           AgentType.builder),
    ("fiduciary-conflict-detector",    "Fiduciary Conflict Detector",     AgentType.builder),
    ("negligent-monitoring-risk-agent","Negligent Monitoring Risk Agent", AgentType.builder),
]

# (id, label, action, tooltip)
_OVERRIDES: list[tuple[str, str, OverrideAction, str]] = [
    ("fire_r1",          "Fire Reversal 1",     OverrideAction.fire_reversal_1,
     "Triggers multi-customer correlation signal (Day 1, t+10s)"),
    ("fire_r2",          "Fire Reversal 2",     OverrideAction.fire_reversal_2,
     "ClearFlow cleared; Nimbus identified as vector (Day 5, t+25s)"),
    ("fire_r3",          "Fire Reversal 3 ★",   OverrideAction.fire_reversal_3,
     "TN DOI subpoena: spawns 6 grandchild cases simultaneously (Day 30, t+45s)"),
    ("fire_r4",          "Fire Reversal 4",     OverrideAction.fire_reversal_4,
     "Fiduciary conflict fires: tri-party HITL gate opens (Day 45, t+75s)"),
    ("fire_r5",          "Fire Reversal 5",     OverrideAction.fire_reversal_5,
     "Litigation cascade: bystander becomes co-defendant (Day 90, t+120s)"),
    ("spawn_grandchildren","Spawn Grandchildren",OverrideAction.spawn_grandchildren,
     "Manually trigger the 6-grandchild fan-spawn (same as Reversal 3)"),
    ("trigger_hitl",     "Trigger HITL Gate",   OverrideAction.trigger_hitl_gate,
     "Open the Fiduciary Conflict HITL gate in Action Center"),
    ("reset_demo",       "Reset Demo",          OverrideAction.reset_demo,
     "Reset all override controls to enabled; clear agent activity"),
]

# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------

def _build_cascade_tree(parent_specs: list[tuple[str, str, str]] | None = None) -> CascadeTree:
    """Build the three-level cascade tree from (slug, display_name, stage) specs.

    parent_specs=None uses the fixture (_PARENTS); live mode passes specs sourced
    from Data Fabric. Master and grandchildren are invariant — grandchildren
    always derive from the same specs as parents, so parent_id never dangles.
    """
    specs = parent_specs if parent_specs is not None else _PARENTS
    master = CaseNode(
        id=_MASTER_ID,
        display_name="ClearFlow Financial Cyber Shockwave",
        stage="Regulatory Response",
        status=CaseStatus.active,
        level=0,
    )
    parents = [
        CaseNode(id=f"case-parent-{slug}", display_name=name, stage=stage,
                 status=CaseStatus.active, parent_id=_MASTER_ID, level=1)
        for slug, name, stage in specs
    ]
    grandchildren = [
        CaseNode(
            id=f"case-grandchild-tn-doi-{slug}",
            display_name=f"TN DOI Obligation — {name}",
            stage="Response Drafting",
            status=CaseStatus.active,
            parent_id=f"case-parent-{slug}",
            level=2,
        )
        for slug, name, _ in specs
        if slug in _PROVIDER_SLUGS
    ]
    return CascadeTree(master=master, parents=parents, grandchildren=grandchildren)


def _build_reversal_timeline() -> list[ReversalEvent]:
    return [
        ReversalEvent(number=n, name=name, day=day,
                      wall_clock_seconds=wc, goal_from=gf, goal_to=gt)
        for n, name, day, wc, gf, gt in _REVERSALS
    ]


def _build_agent_activity() -> list[AgentActivity]:
    return [
        AgentActivity(agent_id=aid, display_name=name,
                      agent_type=atype, status=AgentStatus.idle)
        for aid, name, atype in _AGENTS
    ]


def _build_override_controls() -> list[OverrideControl]:
    return [
        OverrideControl(id=oid, label=label, action=action,
                        enabled=True, tooltip=tip)
        for oid, label, action, tip in _OVERRIDES
    ]


# ---------------------------------------------------------------------------
# Live mode — Data Fabric integration via UiPath SDK
# ---------------------------------------------------------------------------

def _live_entities_service() -> Any:
    """Return an authenticated EntitiesService instance.

    Reads UIPATH_CLIENT_ID / UIPATH_CLIENT_SECRET / UIPATH_BASE_URL from env.
    Raises RuntimeError if required credentials are absent (caught by tests).
    """
    client_id = os.environ.get("UIPATH_CLIENT_ID", "")
    if not client_id:
        raise RuntimeError(
            "UIPATH_CLIENT_ID env var is required for live mode. "
            "Set UIPATH_LIVE=false to use fixture data."
        )
    client_secret = os.environ.get("UIPATH_CLIENT_SECRET", "")
    base_url = os.environ.get("UIPATH_BASE_URL", "")

    from uipath.platform import UiPath  # deferred import — not needed in fixture mode
    client = UiPath(
        client_id=client_id,
        client_secret=client_secret,
        base_url=base_url,
    )
    return client.entities


def _live_parent_specs(entities_svc: Any) -> list[tuple[str, str, str]]:
    """Source parent (slug, display_name, stage) specs from Data Fabric.

    Falls back to the fixture parents when the Provider entity is empty or the
    read fails, so the dashboard always renders the full cascade for the demo.
    """
    try:
        rows: list[dict[str, Any]] = entities_svc.list_records("Provider") or []
    except Exception:
        rows = []
    if not rows:
        return _PARENTS
    return [
        (
            str(r.get("slug", r.get("id", i))),
            r.get("display_name", f"Stakeholder {i}"),
            r.get("stage", "Active"),
        )
        for i, r in enumerate(rows)
    ]


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def build_payload(*, live: bool | None = None) -> DashboardPayload:
    """Return the dashboard payload.

    live=None  — reads UIPATH_LIVE env-var (production default).
    live=False — forces fixture mode regardless of env (use in tests).
    live=True  — reads from UiPath Data Fabric via SDK; requires env credentials.
    """
    use_live = live if live is not None else (
        os.environ.get("UIPATH_LIVE", "").lower() == "true"
    )
    parent_specs = _live_parent_specs(_live_entities_service()) if use_live else None
    return DashboardPayload(
        cascade_tree=_build_cascade_tree(parent_specs),
        reversal_timeline=_build_reversal_timeline(),
        agent_activity=_build_agent_activity(),
        override_controls=_build_override_controls(),
        refreshed_at=datetime.now(tz=timezone.utc).isoformat(),
    )
