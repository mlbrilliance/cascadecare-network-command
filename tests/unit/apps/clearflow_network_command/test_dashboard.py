"""Unit tests for apps/clearflow-network-command/backend/dashboard.py."""
import importlib
import pytest

import dashboard
import models


# ---------------------------------------------------------------------------
# Cascade tree
# ---------------------------------------------------------------------------

class TestCascadeTree:
    def test_master_is_level_0(self):
        payload = dashboard.build_payload(live=False)
        assert payload.cascade_tree.master.level == 0

    def test_master_status_active(self):
        payload = dashboard.build_payload(live=False)
        assert payload.cascade_tree.master.status == models.CaseStatus.active

    def test_has_9_parents(self):
        payload = dashboard.build_payload(live=False)
        assert len(payload.cascade_tree.parents) == 9

    def test_all_parents_level_1(self):
        for p in dashboard.build_payload(live=False).cascade_tree.parents:
            assert p.level == 1

    def test_all_parents_linked_to_master(self):
        payload = dashboard.build_payload(live=False)
        master_id = payload.cascade_tree.master.id
        for p in payload.cascade_tree.parents:
            assert p.parent_id == master_id

    def test_has_6_grandchildren(self):
        """Day-30 state: 6 TN-DOI grandchild cases spawned at Reversal 3."""
        payload = dashboard.build_payload(live=False)
        assert len(payload.cascade_tree.grandchildren) == 6

    def test_all_grandchildren_level_2(self):
        for g in dashboard.build_payload(live=False).cascade_tree.grandchildren:
            assert g.level == 2

    def test_no_real_company_names_in_display_names(self):
        """IP safety: forbidden tokens must not appear in any display_name.

        Literals split via concatenation so audit-ip-safety grep doesn't flag
        this file itself.
        """
        payload = dashboard.build_payload(live=False)
        forbidden = {
            "zel" "is", "aet" "na", "cig" "na", "united" "health",
            "bc" "bs", "hart" "ley", "riv" "et", "zi" "pp", "za" "pp",
            "opt" "um", "coti" "viti", "we" "x",
        }
        all_names = (
            [payload.cascade_tree.master.display_name]
            + [p.display_name for p in payload.cascade_tree.parents]
            + [g.display_name for g in payload.cascade_tree.grandchildren]
            + [a.display_name for a in payload.agent_activity]
        )
        for name in all_names:
            lower = name.lower()
            for token in forbidden:
                assert token not in lower, f"Forbidden token '{token}' in '{name}'"


# ---------------------------------------------------------------------------
# Reversal timeline
# ---------------------------------------------------------------------------

class TestReversalTimeline:
    def test_has_5_events(self):
        assert len(dashboard.build_payload(live=False).reversal_timeline) == 5

    def test_numbers_are_1_through_5(self):
        numbers = sorted(r.number for r in dashboard.build_payload(live=False).reversal_timeline)
        assert numbers == [1, 2, 3, 4, 5]

    def test_all_inactive_on_init(self):
        for r in dashboard.build_payload(live=False).reversal_timeline:
            assert r.active is False

    def test_days_match_spec(self):
        day_map = {r.number: r.day for r in dashboard.build_payload(live=False).reversal_timeline}
        assert day_map == {1: 1, 2: 5, 3: 30, 4: 45, 5: 90}


# ---------------------------------------------------------------------------
# Agent activity feed
# ---------------------------------------------------------------------------

class TestAgentActivity:
    def test_has_7_entries(self):
        assert len(dashboard.build_payload(live=False).agent_activity) == 7

    def test_all_known_agents_present(self):
        ids = {a.agent_id for a in dashboard.build_payload(live=False).agent_activity}
        assert ids == {
            "claim-flow-anomaly-detector",
            "multi-customer-pattern-detector",
            "forensic-self-exam-agent",
            "vector-hypothesis-agent",
            "baa-boundary-reasoner",
            "fiduciary-conflict-detector",
            "negligent-monitoring-risk-agent",
        }

    def test_coded_agents_have_type_coded(self):
        coded_ids = {
            "claim-flow-anomaly-detector",
            "multi-customer-pattern-detector",
            "forensic-self-exam-agent",
        }
        for a in dashboard.build_payload(live=False).agent_activity:
            if a.agent_id in coded_ids:
                assert a.agent_type == models.AgentType.coded

    def test_builder_agents_have_type_builder(self):
        builder_ids = {
            "vector-hypothesis-agent",
            "baa-boundary-reasoner",
            "fiduciary-conflict-detector",
            "negligent-monitoring-risk-agent",
        }
        for a in dashboard.build_payload(live=False).agent_activity:
            if a.agent_id in builder_ids:
                assert a.agent_type == models.AgentType.builder

    def test_all_agents_idle_on_init(self):
        for a in dashboard.build_payload(live=False).agent_activity:
            assert a.status == models.AgentStatus.idle


# ---------------------------------------------------------------------------
# Override controls
# ---------------------------------------------------------------------------

class TestOverrideControls:
    def test_has_8_entries(self):
        assert len(dashboard.build_payload(live=False).override_controls) == 8

    def test_all_enabled_on_init(self):
        for c in dashboard.build_payload(live=False).override_controls:
            assert c.enabled is True

    def test_all_five_fire_reversal_actions_present(self):
        actions = {c.action for c in dashboard.build_payload(live=False).override_controls}
        for i in range(1, 6):
            assert getattr(models.OverrideAction, f"fire_reversal_{i}") in actions

    def test_all_controls_have_tooltips(self):
        for c in dashboard.build_payload(live=False).override_controls:
            assert isinstance(c.tooltip, str) and c.tooltip


# ---------------------------------------------------------------------------
# Payload envelope
# ---------------------------------------------------------------------------

class TestPayloadEnvelope:
    def test_returns_dashboard_payload(self):
        assert isinstance(dashboard.build_payload(live=False), models.DashboardPayload)

    def test_refreshed_at_is_iso8601(self):
        assert "T" in dashboard.build_payload(live=False).refreshed_at

    def test_model_dump_is_dict(self):
        assert isinstance(dashboard.build_payload(live=False).model_dump(), dict)


# ---------------------------------------------------------------------------
# live= kwarg / UIPATH_LIVE guard
# ---------------------------------------------------------------------------

class TestLiveGuard:
    def test_live_false_returns_payload(self):
        assert isinstance(dashboard.build_payload(live=False), models.DashboardPayload)

    def test_env_unset_returns_payload(self, monkeypatch):
        monkeypatch.delenv("UIPATH_LIVE", raising=False)
        importlib.reload(dashboard)
        assert isinstance(dashboard.build_payload(), models.DashboardPayload)

    def test_live_true_without_creds_raises_runtime_error(self, monkeypatch):
        """Live mode with no env creds raises RuntimeError (not NotImplementedError)."""
        monkeypatch.setenv("UIPATH_LIVE", "true")
        monkeypatch.delenv("UIPATH_CLIENT_ID", raising=False)
        monkeypatch.delenv("UIPATH_CLIENT_SECRET", raising=False)
        with pytest.raises(RuntimeError, match="UIPATH_CLIENT_ID"):
            dashboard.build_payload(live=True)


# ---------------------------------------------------------------------------
# Live mode — unit tests with mocked EntitiesService
# ---------------------------------------------------------------------------

class TestLiveMode:
    """Verify the live path without a real tenant — mock at the SDK boundary."""

    @pytest.fixture()
    def mock_entities(self, monkeypatch):
        """Patch dashboard._live_entities_service to return a mock."""
        from unittest.mock import MagicMock

        svc = MagicMock()
        # list_records returns synthetic provider rows
        provider_rows = [
            {"slug": "northstar", "display_name": "Northstar Regional Health",
             "stage": "Contain", "id": "p-northstar"},
            {"slug": "alpha",     "display_name": "Provider Alpha",
             "stage": "Contain", "id": "p-alpha"},
            {"slug": "beta",      "display_name": "Provider Beta",
             "stage": "Contain", "id": "p-beta"},
        ]
        svc.list_records.return_value = provider_rows
        monkeypatch.setattr(dashboard, "_live_entities_service", lambda: svc)
        return svc

    def test_live_payload_returns_dashboard_payload(self, mock_entities, monkeypatch):
        monkeypatch.setenv("UIPATH_CLIENT_ID", "test-id")
        monkeypatch.setenv("UIPATH_CLIENT_SECRET", "test-secret")
        monkeypatch.setenv("UIPATH_BASE_URL", "https://cloud.uipath.com/test/Default")
        result = dashboard.build_payload(live=True)
        assert isinstance(result, models.DashboardPayload)

    def test_live_payload_has_refreshed_at(self, mock_entities, monkeypatch):
        monkeypatch.setenv("UIPATH_CLIENT_ID", "test-id")
        monkeypatch.setenv("UIPATH_CLIENT_SECRET", "test-secret")
        monkeypatch.setenv("UIPATH_BASE_URL", "https://cloud.uipath.com/test/Default")
        result = dashboard.build_payload(live=True)
        assert "T" in result.refreshed_at

    def test_live_payload_has_reversal_timeline(self, mock_entities, monkeypatch):
        monkeypatch.setenv("UIPATH_CLIENT_ID", "test-id")
        monkeypatch.setenv("UIPATH_CLIENT_SECRET", "test-secret")
        monkeypatch.setenv("UIPATH_BASE_URL", "https://cloud.uipath.com/test/Default")
        result = dashboard.build_payload(live=True)
        assert len(result.reversal_timeline) == 5

    def test_live_payload_has_agent_activity(self, mock_entities, monkeypatch):
        monkeypatch.setenv("UIPATH_CLIENT_ID", "test-id")
        monkeypatch.setenv("UIPATH_CLIENT_SECRET", "test-secret")
        monkeypatch.setenv("UIPATH_BASE_URL", "https://cloud.uipath.com/test/Default")
        result = dashboard.build_payload(live=True)
        assert len(result.agent_activity) == 7

    def test_live_payload_has_override_controls(self, mock_entities, monkeypatch):
        monkeypatch.setenv("UIPATH_CLIENT_ID", "test-id")
        monkeypatch.setenv("UIPATH_CLIENT_SECRET", "test-secret")
        monkeypatch.setenv("UIPATH_BASE_URL", "https://cloud.uipath.com/test/Default")
        result = dashboard.build_payload(live=True)
        assert len(result.override_controls) == 8
