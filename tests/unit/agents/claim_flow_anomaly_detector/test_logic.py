"""Slice 009 — Claim Flow Anomaly Detector: deterministic-core tests (TDD, test-first).

The agent's deterministic core is imported BY PATH (importlib) so these tests run
under the repo-root `uv run pytest` without the agent's own venv or any UiPath
auth. Only the pure functions / pydantic models are exercised here; the optional
SDK LLM-enrichment hook is verified at deploy time, not in this suite.

Coverage: severity thresholds, monotonicity (bigger drop -> higher score),
boundary cases, derivation of claim_drop_pct from baseline/observed volume, and
alignment with the provider-claim-anomaly event contract output fields.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from types import ModuleType

# The provider-claim-anomaly contract routes when anomaly_score >= this value.
CONTRACT_TRIGGER_SCORE = 0.7

REPO_ROOT = Path(__file__).parents[4]
AGENT_PY = REPO_ROOT / "agents" / "claim-flow-anomaly-detector" / "agent.py"


def _load_agent() -> ModuleType:
    """Load agent.py by file path (dir name has hyphens -> not importable normally)."""
    spec = importlib.util.spec_from_file_location("cfad_agent_under_test", AGENT_PY)
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
        # Reaching here means exec_module succeeded with no UiPath() instantiation.
        assert hasattr(agent, "classify_anomaly")
        assert hasattr(agent, "Input")
        assert hasattr(agent, "Output")
        assert hasattr(agent, "main")


class TestScoreThresholds:
    @pytest.mark.parametrize(
        ("drop_pct", "expected_severity"),
        [
            (0.0, "none"),
            (10.0, "none"),
            (24.9, "none"),
            (25.0, "low"),
            (40.0, "low"),
            (49.9, "low"),
            (50.0, "elevated"),
            (60.0, "elevated"),
            (69.9, "elevated"),
            (70.0, "critical"),
            (91.0, "critical"),
            (100.0, "critical"),
        ],
    )
    def test_severity_thresholds(
        self, agent: ModuleType, drop_pct: float, expected_severity: str
    ) -> None:
        result = agent.classify_anomaly(agent.Input(provider_id="northstar", claim_drop_pct=drop_pct))
        assert result.severity == expected_severity

    def test_critical_threshold_aligns_with_contract_trigger(self, agent: ModuleType) -> None:
        # The provider-claim-anomaly contract routes when anomaly_score >= 0.7.
        # The 'critical' severity boundary must land exactly there.
        result = agent.classify_anomaly(agent.Input(provider_id="alpha", claim_drop_pct=70.0))
        assert result.anomaly_score >= CONTRACT_TRIGGER_SCORE
        assert result.severity == "critical"


class TestScoreRangeAndMonotonicity:
    @pytest.mark.parametrize("drop_pct", [0.0, 5.0, 25.0, 50.0, 73.3, 100.0])
    def test_score_in_unit_interval(self, agent: ModuleType, drop_pct: float) -> None:
        result = agent.classify_anomaly(agent.Input(provider_id="beta", claim_drop_pct=drop_pct))
        assert 0.0 <= result.anomaly_score <= 1.0

    def test_score_is_monotonic_in_drop(self, agent: ModuleType) -> None:
        drops = [0.0, 10.0, 25.0, 50.0, 70.0, 91.0, 100.0]
        scores = [
            agent.classify_anomaly(agent.Input(provider_id="gamma", claim_drop_pct=d)).anomaly_score
            for d in drops
        ]
        assert scores == sorted(scores)
        assert scores[-1] > scores[0]


class TestBoundaryCases:
    def test_zero_drop_is_normal(self, agent: ModuleType) -> None:
        result = agent.classify_anomaly(agent.Input(provider_id="delta", claim_drop_pct=0.0))
        assert result.anomaly_score == 0.0
        assert result.severity == "none"

    def test_full_drop_is_certain_anomaly(self, agent: ModuleType) -> None:
        result = agent.classify_anomaly(agent.Input(provider_id="epsilon", claim_drop_pct=100.0))
        assert result.anomaly_score == 1.0
        assert result.severity == "critical"

    def test_drop_pct_clamped_above_100(self, agent: ModuleType) -> None:
        result = agent.classify_anomaly(agent.Input(provider_id="northstar", claim_drop_pct=140.0))
        assert result.anomaly_score == 1.0
        assert result.severity == "critical"

    def test_negative_drop_clamped_to_zero(self, agent: ModuleType) -> None:
        result = agent.classify_anomaly(agent.Input(provider_id="northstar", claim_drop_pct=-5.0))
        assert result.anomaly_score == 0.0
        assert result.severity == "none"


class TestVolumeDerivation:
    def test_drop_pct_derived_from_volumes_when_absent(self, agent: ModuleType) -> None:
        # 1000 baseline, 100 observed => 90% drop.
        result = agent.classify_anomaly(
            agent.Input(
                provider_id="alpha",
                baseline_claim_volume=1000,
                observed_claim_volume=100,
            )
        )
        assert result.claim_drop_pct == pytest.approx(90.0)
        assert result.severity == "critical"

    def test_explicit_drop_pct_wins_over_volumes(self, agent: ModuleType) -> None:
        result = agent.classify_anomaly(
            agent.Input(
                provider_id="beta",
                claim_drop_pct=10.0,
                baseline_claim_volume=1000,
                observed_claim_volume=100,
            )
        )
        assert result.claim_drop_pct == pytest.approx(10.0)
        assert result.severity == "none"

    def test_observed_above_baseline_is_no_drop(self, agent: ModuleType) -> None:
        result = agent.classify_anomaly(
            agent.Input(
                provider_id="gamma",
                baseline_claim_volume=500,
                observed_claim_volume=600,
            )
        )
        assert result.claim_drop_pct == 0.0
        assert result.severity == "none"

    def test_zero_baseline_is_safe(self, agent: ModuleType) -> None:
        # Avoid divide-by-zero: no baseline => cannot establish a drop => 0%.
        result = agent.classify_anomaly(
            agent.Input(
                provider_id="delta",
                baseline_claim_volume=0,
                observed_claim_volume=0,
            )
        )
        assert result.claim_drop_pct == 0.0
        assert result.severity == "none"


class TestContractAlignment:
    def test_output_carries_contract_fields(self, agent: ModuleType) -> None:
        result = agent.classify_anomaly(
            agent.Input(provider_id="northstar", claim_drop_pct=91.0)
        )
        # provider-claim-anomaly contract requires: provider_id, claim_drop_pct, anomaly_score
        assert result.provider_id == "northstar"
        assert result.claim_drop_pct == pytest.approx(91.0)
        assert 0.0 <= result.anomaly_score <= 1.0
        assert result.severity in {"none", "low", "elevated", "critical"}

    def test_main_entrypoint_returns_output(self, agent: ModuleType) -> None:
        out = agent.main(agent.Input(provider_id="alpha", claim_drop_pct=80.0))
        assert isinstance(out, agent.Output)
        assert out.provider_id == "alpha"
        assert out.severity == "critical"
