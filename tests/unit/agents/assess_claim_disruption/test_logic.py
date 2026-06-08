"""Mock coded process — Assess Claim Disruption & Liquidity: deterministic-core tests."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from types import ModuleType

REPO_ROOT = Path(__file__).parents[4]
AGENT_PY = REPO_ROOT / "agents" / "assess-claim-disruption" / "agent.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("assess_claim_disruption_uut", AGENT_PY)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def agent() -> ModuleType:
    assert AGENT_PY.exists(), f"agent.py not found at {AGENT_PY}"
    return _load()


def test_critical_disruption(agent: ModuleType) -> None:
    out = agent.main(
        agent.Input(stakeholder_id="northstar", baseline_claim_volume=1000, observed_claim_volume=200,
                    business_continuity_runway_days=12)
    )
    assert out.disruption_score == 0.8
    assert out.impact_tier == "critical"
    assert out.liquidity_runway_days == 12
    assert out.error_type == ""


def test_no_disruption_when_volumes_absent(agent: ModuleType) -> None:
    out = agent.main(agent.Input(stakeholder_id="alpha"))
    assert out.disruption_score == 0.0
    assert out.impact_tier == "none"


def test_monotonic(agent: ModuleType) -> None:
    small = agent.main(agent.Input(baseline_claim_volume=100, observed_claim_volume=90))
    large = agent.main(agent.Input(baseline_claim_volume=100, observed_claim_volume=10))
    assert large.disruption_score > small.disruption_score


def test_empty_inputs_complete(agent: ModuleType) -> None:
    out = agent.main(agent.Input())
    assert out.error_type == "" and out.impact_tier == "none"
