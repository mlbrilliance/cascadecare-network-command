"""Slice 009 — Multi-Customer Pattern Detector: deterministic-core tests (TDD).

Imported BY PATH so it runs under repo-root `uv run pytest` with no UiPath auth.
Covers the cascade-signal rule (>=3 anomalous providers), correlation_score
computation, empty input, dedup, and multi-customer-correlation contract fields.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from types import ModuleType

# Cascade fires once this many distinct providers are anomalous.
CASCADE_MIN = 3
# baseline_likelihood_pct ceiling (a coincidence is 100% likely with no pattern).
LIKELIHOOD_MAX_PCT = 100.0

REPO_ROOT = Path(__file__).parents[4]
AGENT_PY = REPO_ROOT / "agents" / "multi-customer-pattern-detector" / "agent.py"


def _load_agent() -> ModuleType:
    spec = importlib.util.spec_from_file_location("mcpd_agent_under_test", AGENT_PY)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def agent() -> ModuleType:
    assert AGENT_PY.exists(), f"agent.py not found at {AGENT_PY}"
    return _load_agent()


def _pr(agent: ModuleType, provider_id: str, score: float) -> object:
    return agent.ProviderResult(provider_id=provider_id, anomaly_score=score)


class TestImportsWithoutAuth:
    def test_module_imports_without_uipath_auth(self, agent: ModuleType) -> None:
        assert hasattr(agent, "correlate")
        assert hasattr(agent, "Input")
        assert hasattr(agent, "Output")
        assert hasattr(agent, "ProviderResult")
        assert hasattr(agent, "main")


class TestCascadeSignal:
    def test_two_anomalous_no_signal(self, agent: ModuleType) -> None:
        result = agent.correlate(
            agent.Input(
                simulated_day=1,
                provider_results=[
                    _pr(agent, "northstar", 0.9),
                    _pr(agent, "alpha", 0.85),
                ],
            )
        )
        assert result.cascade_signal is False
        assert set(result.affected_provider_ids) == {"northstar", "alpha"}

    def test_three_anomalous_fires_signal(self, agent: ModuleType) -> None:
        result = agent.correlate(
            agent.Input(
                simulated_day=1,
                provider_results=[
                    _pr(agent, "northstar", 0.9),
                    _pr(agent, "alpha", 0.85),
                    _pr(agent, "beta", 0.8),
                ],
            )
        )
        assert result.cascade_signal is True
        assert set(result.affected_provider_ids) == {"northstar", "alpha", "beta"}

    def test_below_threshold_providers_excluded(self, agent: ModuleType) -> None:
        # Two strong + two weak: only the strong count as affected; no cascade.
        result = agent.correlate(
            agent.Input(
                simulated_day=2,
                provider_results=[
                    _pr(agent, "northstar", 0.95),
                    _pr(agent, "alpha", 0.72),
                    _pr(agent, "beta", 0.3),
                    _pr(agent, "gamma", 0.1),
                ],
            )
        )
        assert set(result.affected_provider_ids) == {"northstar", "alpha"}
        assert result.cascade_signal is False

    def test_threshold_boundary_included(self, agent: ModuleType) -> None:
        # anomaly_score exactly 0.7 counts as anomalous (>= threshold).
        result = agent.correlate(
            agent.Input(
                simulated_day=1,
                provider_results=[
                    _pr(agent, "northstar", 0.7),
                    _pr(agent, "alpha", 0.7),
                    _pr(agent, "beta", 0.7),
                ],
            )
        )
        assert len(result.affected_provider_ids) == CASCADE_MIN
        assert result.cascade_signal is True


class TestCorrelationScore:
    def test_correlation_score_is_mean_of_anomalous(self, agent: ModuleType) -> None:
        result = agent.correlate(
            agent.Input(
                simulated_day=1,
                provider_results=[
                    _pr(agent, "northstar", 0.8),
                    _pr(agent, "alpha", 0.9),
                    _pr(agent, "beta", 1.0),
                    _pr(agent, "gamma", 0.2),  # excluded from mean
                ],
            )
        )
        assert result.correlation_score == pytest.approx((0.8 + 0.9 + 1.0) / 3)

    def test_correlation_score_in_unit_interval(self, agent: ModuleType) -> None:
        result = agent.correlate(
            agent.Input(
                simulated_day=1,
                provider_results=[
                    _pr(agent, "northstar", 0.71),
                    _pr(agent, "alpha", 0.99),
                ],
            )
        )
        assert 0.0 <= result.correlation_score <= 1.0

    def test_no_anomalous_yields_zero_score(self, agent: ModuleType) -> None:
        result = agent.correlate(
            agent.Input(
                simulated_day=1,
                provider_results=[
                    _pr(agent, "northstar", 0.1),
                    _pr(agent, "alpha", 0.4),
                ],
            )
        )
        assert result.correlation_score == 0.0
        assert result.affected_provider_ids == []
        assert result.cascade_signal is False


class TestEmptyAndDedup:
    def test_empty_input(self, agent: ModuleType) -> None:
        result = agent.correlate(agent.Input(simulated_day=0, provider_results=[]))
        assert result.affected_provider_ids == []
        assert result.correlation_score == 0.0
        assert result.cascade_signal is False

    def test_duplicate_providers_deduped_highest_kept(self, agent: ModuleType) -> None:
        # Same provider reported twice; dedup so it is not double-counted toward the >=3 rule.
        result = agent.correlate(
            agent.Input(
                simulated_day=1,
                provider_results=[
                    _pr(agent, "northstar", 0.8),
                    _pr(agent, "northstar", 0.95),
                    _pr(agent, "alpha", 0.9),
                ],
            )
        )
        assert sorted(result.affected_provider_ids) == ["alpha", "northstar"]
        assert result.cascade_signal is False


class TestContractAlignment:
    def test_baseline_likelihood_decreases_with_more_providers(self, agent: ModuleType) -> None:
        small = agent.correlate(
            agent.Input(
                simulated_day=1,
                provider_results=[_pr(agent, "northstar", 0.9), _pr(agent, "alpha", 0.9)],
            )
        )
        big = agent.correlate(
            agent.Input(
                simulated_day=1,
                provider_results=[
                    _pr(agent, "northstar", 0.9),
                    _pr(agent, "alpha", 0.9),
                    _pr(agent, "beta", 0.9),
                    _pr(agent, "gamma", 0.9),
                ],
            )
        )
        assert big.baseline_likelihood_pct < small.baseline_likelihood_pct
        assert 0.0 <= big.baseline_likelihood_pct <= LIKELIHOOD_MAX_PCT

    def test_cascade_signal_sets_sub_one_percent_likelihood(self, agent: ModuleType) -> None:
        # The contract fires Reversal 1 when baseline_likelihood_pct <= 1.0; a
        # cascade (>=3 correlated) must drive likelihood into that sub-1% band.
        result = agent.correlate(
            agent.Input(
                simulated_day=1,
                provider_results=[
                    _pr(agent, "northstar", 0.95),
                    _pr(agent, "alpha", 0.9),
                    _pr(agent, "beta", 0.92),
                ],
            )
        )
        assert result.cascade_signal is True
        assert result.baseline_likelihood_pct <= 1.0

    def test_main_entrypoint_returns_output(self, agent: ModuleType) -> None:
        out = agent.main(
            agent.Input(
                simulated_day=1,
                provider_results=[
                    _pr(agent, "northstar", 0.9),
                    _pr(agent, "alpha", 0.9),
                    _pr(agent, "beta", 0.9),
                ],
            )
        )
        assert isinstance(out, agent.Output)
        assert out.cascade_signal is True
