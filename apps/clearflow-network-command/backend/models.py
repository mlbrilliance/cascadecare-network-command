"""Pydantic models for the ClearFlow Network Command dashboard backend.

These are the shared data contracts between the Coded App backend and the
UiPath Apps frontend. All display names must use only fictional entities
defined in CONTEXT.md (ClearFlow, Northstar, Apex Health Plan, etc.).
"""
from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class CaseStatus(str, Enum):
    active = "active"
    suspended = "suspended"
    completed = "completed"
    pending = "pending"


class AgentType(str, Enum):
    coded = "coded"
    builder = "builder"


class AgentStatus(str, Enum):
    idle = "idle"
    running = "running"
    completed = "completed"
    error = "error"


class OverrideAction(str, Enum):
    fire_reversal_1 = "fire_reversal_1"
    fire_reversal_2 = "fire_reversal_2"
    fire_reversal_3 = "fire_reversal_3"
    fire_reversal_4 = "fire_reversal_4"
    fire_reversal_5 = "fire_reversal_5"
    spawn_grandchildren = "spawn_grandchildren"
    trigger_hitl_gate = "trigger_hitl_gate"
    reset_demo = "reset_demo"


class CaseNode(BaseModel):
    id: str
    display_name: str
    stage: str
    status: CaseStatus
    parent_id: Optional[str] = None
    level: int


class ReversalEvent(BaseModel):
    number: int
    name: str
    day: int
    wall_clock_seconds: int
    goal_from: str
    goal_to: str
    active: bool = False


class AgentActivity(BaseModel):
    agent_id: str
    display_name: str
    agent_type: AgentType
    status: AgentStatus = AgentStatus.idle
    last_output: Optional[str] = None
    invocation_count: int = 0
    last_invoked_at: Optional[str] = None


class OverrideControl(BaseModel):
    id: str
    label: str
    action: OverrideAction
    enabled: bool = True
    tooltip: str


class CascadeTree(BaseModel):
    master: CaseNode
    parents: List[CaseNode]
    grandchildren: List[CaseNode]


class DashboardPayload(BaseModel):
    cascade_tree: CascadeTree
    reversal_timeline: List[ReversalEvent]
    agent_activity: List[AgentActivity]
    override_controls: List[OverrideControl]
    refreshed_at: str
