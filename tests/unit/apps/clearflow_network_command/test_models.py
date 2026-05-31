"""Unit tests for apps/clearflow-network-command/backend/models.py."""
import pytest

import models


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TestCaseStatus:
    def test_valid_values(self):
        assert models.CaseStatus.active == "active"
        assert models.CaseStatus.suspended == "suspended"
        assert models.CaseStatus.completed == "completed"
        assert models.CaseStatus.pending == "pending"

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            models.CaseStatus("nonexistent")


class TestAgentType:
    def test_valid_values(self):
        assert models.AgentType.coded == "coded"
        assert models.AgentType.builder == "builder"


class TestAgentStatus:
    def test_valid_values(self):
        assert models.AgentStatus.idle == "idle"
        assert models.AgentStatus.running == "running"
        assert models.AgentStatus.completed == "completed"
        assert models.AgentStatus.error == "error"


class TestOverrideAction:
    def test_all_reversals_present(self):
        for i in range(1, 6):
            assert hasattr(models.OverrideAction, f"fire_reversal_{i}")

    def test_spawn_grandchildren(self):
        assert models.OverrideAction.spawn_grandchildren == "spawn_grandchildren"

    def test_trigger_hitl_gate(self):
        assert models.OverrideAction.trigger_hitl_gate == "trigger_hitl_gate"

    def test_reset_demo(self):
        assert models.OverrideAction.reset_demo == "reset_demo"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class TestCaseNode:
    def test_minimal_construction(self):
        node = models.CaseNode(
            id="case-001", display_name="ClearFlow Financial Cyber Shockwave",
            stage="Triage", status=models.CaseStatus.active, level=0,
        )
        assert node.id == "case-001"
        assert node.level == 0
        assert node.parent_id is None

    def test_with_parent_id(self):
        node = models.CaseNode(
            id="case-002", display_name="Northstar Regional Health",
            stage="Contain", status=models.CaseStatus.active,
            parent_id="case-001", level=1,
        )
        assert node.parent_id == "case-001"

    def test_invalid_status_raises(self):
        with pytest.raises((ValueError, Exception)):
            models.CaseNode(id="x", display_name="x", stage="x",
                            status="bad_status", level=0)


class TestReversalEvent:
    def test_construction(self):
        r = models.ReversalEvent(
            number=1, name="Multi-customer correlation", day=1,
            wall_clock_seconds=10,
            goal_from="Assist isolated customers",
            goal_to="Determine if ClearFlow is the vector",
        )
        assert r.number == 1
        assert r.active is False

    def test_number_range(self):
        for n in range(1, 6):
            r = models.ReversalEvent(
                number=n, name=f"R{n}", day=n, wall_clock_seconds=n * 10,
                goal_from="a", goal_to="b",
            )
            assert r.number == n


class TestAgentActivity:
    def test_optional_fields_default_to_none(self):
        a = models.AgentActivity(
            agent_id="claim-flow-anomaly-detector",
            display_name="Claim Flow Anomaly Detector",
            agent_type=models.AgentType.coded,
            status=models.AgentStatus.idle,
        )
        assert a.last_output is None
        assert a.last_invoked_at is None

    def test_with_output(self):
        a = models.AgentActivity(
            agent_id="vector-hypothesis-agent",
            display_name="Vector Hypothesis Agent",
            agent_type=models.AgentType.builder,
            status=models.AgentStatus.completed,
            last_output="Vector: nimbus (confidence 0.87)",
            invocation_count=1,
            last_invoked_at="2026-05-30T00:00:00Z",
        )
        assert a.last_output == "Vector: nimbus (confidence 0.87)"


class TestOverrideControl:
    def test_construction(self):
        c = models.OverrideControl(
            id="fire_r1", label="Fire Reversal 1",
            action=models.OverrideAction.fire_reversal_1,
            enabled=True, tooltip="Triggers multi-customer correlation signal",
        )
        assert c.enabled is True

    def test_can_disable(self):
        c = models.OverrideControl(
            id="fire_r3", label="Fire Reversal 3 ★",
            action=models.OverrideAction.fire_reversal_3,
            enabled=False, tooltip="Already fired",
        )
        assert c.enabled is False


class TestCascadeTree:
    def test_construction(self):
        master = models.CaseNode(
            id="master", display_name="Master", stage="S",
            status=models.CaseStatus.active, level=0,
        )
        tree = models.CascadeTree(master=master, parents=[], grandchildren=[])
        assert tree.master.id == "master"
        assert tree.parents == []


class TestDashboardPayload:
    def test_construction(self):
        master = models.CaseNode(
            id="m", display_name="M", stage="S",
            status=models.CaseStatus.active, level=0,
        )
        payload = models.DashboardPayload(
            cascade_tree=models.CascadeTree(master=master, parents=[], grandchildren=[]),
            reversal_timeline=[],
            agent_activity=[],
            override_controls=[],
            refreshed_at="2026-05-30T00:00:00Z",
        )
        assert payload.refreshed_at == "2026-05-30T00:00:00Z"

    def test_model_dump_is_dict(self):
        master = models.CaseNode(
            id="m", display_name="M", stage="S",
            status=models.CaseStatus.active, level=0,
        )
        payload = models.DashboardPayload(
            cascade_tree=models.CascadeTree(master=master, parents=[], grandchildren=[]),
            reversal_timeline=[], agent_activity=[], override_controls=[],
            refreshed_at="2026-05-30T00:00:00Z",
        )
        d = payload.model_dump()
        assert isinstance(d, dict)
        assert "cascade_tree" in d
