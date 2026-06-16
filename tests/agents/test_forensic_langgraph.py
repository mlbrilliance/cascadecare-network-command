"""Tests for the LangGraph forensic-self-exam-agent.

The graph is exercised via its compiled invoke() interface. All assertions are
offline — no UiPath auth required. The LLM enrich_node is exercised through
a monkeypatch so the happy path is verified without network calls.
"""

from __future__ import annotations

import importlib
import sys
import types
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


def _load_agent():
    """Import the agent module freshly (avoids stale module cache between tests)."""
    mod_path = str(
        __import__("pathlib").Path(__file__).parent.parent.parent
        / "agents"
        / "forensic-self-exam-agent-langgraph"
    )
    if mod_path not in sys.path:
        sys.path.insert(0, mod_path)
    import importlib
    if "agent" in sys.modules:
        del sys.modules["agent"]
    return importlib.import_module("agent")


@pytest.fixture()
def agent():
    return _load_agent()


def invoke(agent_mod, inp: dict[str, Any]) -> dict[str, Any]:
    return agent_mod.graph.invoke(inp)


# ── Routing correctness ──────────────────────────────────────────────────────

class TestRouting:
    def test_clearflow_indicators_routes_vector_hypothesis(self, agent):
        result = invoke(agent, {"clearflow_indicators": 2, "nimbus_indicators": 0, "clearflow_self_victim": False})
        assert result["route_to"] == "vector-hypothesis"
        assert result["clearflow_vector_status"] == "unknown"

    def test_nimbus_only_routes_baa_boundary_cleared(self, agent):
        result = invoke(agent, {"clearflow_indicators": 0, "nimbus_indicators": 3, "clearflow_self_victim": False})
        assert result["route_to"] == "baa-boundary"
        assert result["clearflow_vector_status"] == "cleared"

    def test_nimbus_only_self_victim_routes_baa_co_victim(self, agent):
        result = invoke(agent, {"clearflow_indicators": 0, "nimbus_indicators": 1, "clearflow_self_victim": True})
        assert result["route_to"] == "baa-boundary"
        assert result["clearflow_vector_status"] == "co-victim"

    def test_no_indicators_routes_escalate(self, agent):
        result = invoke(agent, {"clearflow_indicators": 0, "nimbus_indicators": 0, "clearflow_self_victim": False})
        assert result["route_to"] == "escalate"
        assert result["clearflow_vector_status"] == "unknown"

    def test_clearflow_dominates_over_nimbus(self, agent):
        result = invoke(agent, {"clearflow_indicators": 1, "nimbus_indicators": 5, "clearflow_self_victim": True})
        assert result["route_to"] == "vector-hypothesis"
        assert result["clearflow_vector_status"] == "unknown"


# ── Negative count clamping ──────────────────────────────────────────────────

class TestClamping:
    def test_negative_clearflow_clamped_to_zero(self, agent):
        result = invoke(agent, {"clearflow_indicators": -3, "nimbus_indicators": 2, "clearflow_self_victim": False})
        assert result["route_to"] == "baa-boundary"

    def test_negative_nimbus_clamped_to_zero(self, agent):
        result = invoke(agent, {"clearflow_indicators": 0, "nimbus_indicators": -1, "clearflow_self_victim": False})
        assert result["route_to"] == "escalate"

    def test_both_negative_clamped_to_escalate(self, agent):
        result = invoke(agent, {"clearflow_indicators": -5, "nimbus_indicators": -10, "clearflow_self_victim": True})
        assert result["route_to"] == "escalate"


# ── Conditional LLM enrichment ───────────────────────────────────────────────

class TestLLMEnrichment:
    def test_escalate_path_skips_llm(self, agent):
        """escalate → rationale is empty, no LLM call attempted."""
        result = invoke(agent, {"clearflow_indicators": 0, "nimbus_indicators": 0, "clearflow_self_victim": False})
        assert result["route_to"] == "escalate"
        assert result["rationale"] == ""

    def test_llm_unavailable_returns_empty_rationale(self, agent):
        """LLM import failure → graceful empty rationale, error surfaced, no exception propagated."""
        with patch.dict("sys.modules", {"uipath.llm_gateway": None}):
            result = invoke(agent, {"clearflow_indicators": 0, "nimbus_indicators": 2, "clearflow_self_victim": False})
        assert result["route_to"] == "baa-boundary"
        assert result["rationale"] == ""
        # The import failure must NOT be swallowed silently — it is surfaced.
        assert result["error_type"] != ""
        assert result["error_message"] != ""

    def test_llm_called_on_non_escalate_path(self, agent):
        """Non-escalate path attempts LLM enrichment (mocked to return a string)."""
        mock_service = MagicMock()
        mock_service.chat_completions.return_value = "ClearFlow is cleared; Nimbus is the vector."

        mock_module = types.ModuleType("uipath.llm_gateway")
        mock_module.UiPathOpenAIService = MagicMock(return_value=mock_service)

        with patch.dict("sys.modules", {"uipath.llm_gateway": mock_module}):
            result = invoke(agent, {"clearflow_indicators": 0, "nimbus_indicators": 1, "clearflow_self_victim": False})

        assert result["route_to"] == "baa-boundary"
        assert "ClearFlow" in result["rationale"]


# ── Exception surfacing (Criterion-3: enrichment failures are not silent) ────

class TestLLMErrorSurfacing:
    def test_llm_runtime_failure_surfaces_error_metadata(self, agent):
        """LLM Gateway failure (e.g. 520) → routing intact, rationale empty, error surfaced.

        The enrichment is advisory: a Gateway failure must NOT fail the graph or
        change the route, but it must NOT be swallowed silently either.
        """
        mock_service = MagicMock()
        mock_service.chat_completions.side_effect = RuntimeError("LLM Gateway 520")

        mock_module = types.ModuleType("uipath.llm_gateway")
        mock_module.UiPathOpenAIService = MagicMock(return_value=mock_service)

        with patch.dict("sys.modules", {"uipath.llm_gateway": mock_module}):
            result = invoke(agent, {"clearflow_indicators": 0, "nimbus_indicators": 1, "clearflow_self_victim": False})

        # Routing is authoritative and untouched by the enrichment failure.
        assert result["route_to"] == "baa-boundary"
        assert result["clearflow_vector_status"] == "cleared"
        # Advisory rationale failed → empty, but the error is surfaced structurally.
        assert result["rationale"] == ""
        assert result["error_type"] == "RuntimeError"
        assert "520" in result["error_message"]

    def test_happy_path_has_empty_error_metadata(self, agent):
        """Successful enrichment → no false-positive error surfaced."""
        mock_service = MagicMock()
        mock_service.chat_completions.return_value = "Nimbus is the vector."

        mock_module = types.ModuleType("uipath.llm_gateway")
        mock_module.UiPathOpenAIService = MagicMock(return_value=mock_service)

        with patch.dict("sys.modules", {"uipath.llm_gateway": mock_module}):
            result = invoke(agent, {"clearflow_indicators": 0, "nimbus_indicators": 1, "clearflow_self_victim": False})

        assert result["rationale"] != ""
        assert result["error_type"] == ""
        assert result["error_message"] == ""

    def test_escalate_path_has_empty_error_metadata(self, agent):
        """escalate skips enrich_node entirely → error fields stay empty (no false error)."""
        result = invoke(agent, {"clearflow_indicators": 0, "nimbus_indicators": 0, "clearflow_self_victim": False})
        assert result["route_to"] == "escalate"
        assert result["error_type"] == ""
        assert result["error_message"] == ""


# ── Graph structure ──────────────────────────────────────────────────────────

class TestGraphStructure:
    def test_graph_is_compiled(self, agent):
        """Module must expose a compiled graph (has .invoke())."""
        assert hasattr(agent, "graph")
        assert callable(agent.graph.invoke)

    def test_state_has_expected_keys(self, agent):
        result = invoke(agent, {"clearflow_indicators": 0, "nimbus_indicators": 0, "clearflow_self_victim": False})
        for key in ("route_to", "clearflow_vector_status", "rationale", "error_type", "error_message"):
            assert key in result

    def test_default_inputs(self, agent):
        """All inputs have defaults — empty dict should not raise."""
        result = invoke(agent, {})
        assert result["route_to"] == "escalate"
