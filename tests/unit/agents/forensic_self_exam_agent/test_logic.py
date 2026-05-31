"""Slice 009 — Forensic Self-Exam Agent: deterministic-core tests (TDD).

Imported BY PATH so it runs under repo-root `uv run pytest` with no UiPath auth.
Covers the routing table (clearflow vs nimbus evidence flags), the
clearflow_vector_status determination, and default/unknown handling.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from types import ModuleType

REPO_ROOT = Path(__file__).parents[4]
AGENT_PY = REPO_ROOT / "agents" / "forensic-self-exam-agent" / "agent.py"

VALID_ROUTES = {"vector-hypothesis", "baa-boundary", "escalate"}
VALID_STATUS = {"unknown", "cleared", "co-victim"}


def _load_agent() -> ModuleType:
    spec = importlib.util.spec_from_file_location("fse_agent_under_test", AGENT_PY)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def agent() -> ModuleType:
    assert AGENT_PY.exists(), f"agent.py not found at {AGENT_PY}"
    return _load_agent()


class TestImportsWithoutAuth:
    def test_module_imports_without_uipath_auth(self, agent: ModuleType) -> None:
        assert hasattr(agent, "route_investigation")
        assert hasattr(agent, "Input")
        assert hasattr(agent, "Output")
        assert hasattr(agent, "main")


class TestRoutingTable:
    def test_clearflow_indicators_route_to_vector_hypothesis(self, agent: ModuleType) -> None:
        # Any internal indicator => must keep investigating own systems first.
        result = agent.route_investigation(
            agent.Input(clearflow_indicators=2, nimbus_indicators=0)
        )
        assert result.route_to == "vector-hypothesis"
        assert result.clearflow_vector_status == "unknown"

    def test_clearflow_indicators_dominate_even_with_nimbus(self, agent: ModuleType) -> None:
        # Internal evidence is never cleared while indicators remain, even if Nimbus also shows up.
        result = agent.route_investigation(
            agent.Input(clearflow_indicators=1, nimbus_indicators=5)
        )
        assert result.route_to == "vector-hypothesis"
        assert result.clearflow_vector_status == "unknown"

    def test_nimbus_only_clears_clearflow_routes_to_baa(self, agent: ModuleType) -> None:
        result = agent.route_investigation(
            agent.Input(clearflow_indicators=0, nimbus_indicators=3)
        )
        assert result.route_to == "baa-boundary"
        assert result.clearflow_vector_status == "cleared"

    def test_nimbus_with_self_victim_flag_is_co_victim(self, agent: ModuleType) -> None:
        # Cleared as the vector but ClearFlow's own systems were also hit -> co-victim.
        result = agent.route_investigation(
            agent.Input(
                clearflow_indicators=0,
                nimbus_indicators=3,
                clearflow_self_victim=True,
            )
        )
        assert result.route_to == "baa-boundary"
        assert result.clearflow_vector_status == "co-victim"

    def test_no_evidence_escalates(self, agent: ModuleType) -> None:
        result = agent.route_investigation(
            agent.Input(clearflow_indicators=0, nimbus_indicators=0)
        )
        assert result.route_to == "escalate"
        assert result.clearflow_vector_status == "unknown"


class TestDefaultsAndBounds:
    def test_defaults_are_zero_and_escalate(self, agent: ModuleType) -> None:
        # No fields supplied -> safe default: nothing known, escalate.
        result = agent.route_investigation(agent.Input())
        assert result.route_to == "escalate"
        assert result.clearflow_vector_status == "unknown"

    @pytest.mark.parametrize(
        ("cf", "nb"),
        [(0, 0), (1, 0), (0, 1), (5, 5), (3, 0), (0, 7)],
    )
    def test_outputs_always_in_valid_domains(self, agent: ModuleType, cf: int, nb: int) -> None:
        result = agent.route_investigation(
            agent.Input(clearflow_indicators=cf, nimbus_indicators=nb)
        )
        assert result.route_to in VALID_ROUTES
        assert result.clearflow_vector_status in VALID_STATUS

    def test_negative_indicators_treated_as_zero(self, agent: ModuleType) -> None:
        # Defensive: a negative count means "no evidence".
        result = agent.route_investigation(
            agent.Input(clearflow_indicators=-3, nimbus_indicators=-1)
        )
        assert result.route_to == "escalate"
        assert result.clearflow_vector_status == "unknown"

    def test_self_victim_flag_ignored_when_not_cleared(self, agent: ModuleType) -> None:
        # While ClearFlow indicators remain, the self-victim flag must not flip status.
        result = agent.route_investigation(
            agent.Input(
                clearflow_indicators=2,
                nimbus_indicators=0,
                clearflow_self_victim=True,
            )
        )
        assert result.clearflow_vector_status == "unknown"
        assert result.route_to == "vector-hypothesis"


class TestEntrypoint:
    def test_main_entrypoint_returns_output(self, agent: ModuleType) -> None:
        out = agent.main(agent.Input(clearflow_indicators=0, nimbus_indicators=4))
        assert isinstance(out, agent.Output)
        assert out.route_to == "baa-boundary"
        assert out.clearflow_vector_status == "cleared"
