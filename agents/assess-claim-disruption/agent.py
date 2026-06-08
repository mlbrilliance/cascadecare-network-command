"""Assess Claim Disruption & Liquidity — UiPath Coded Function (mock process).

Deterministic mock for the clearflow-stakeholder-parent "Impact Assessment" stage.
Scores a provider's claim-flow disruption and liquidity runway so the child case
walks. Pure stdlib + pydantic; no LLM/SDK/randomness; deterministic in the inputs.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

_ELEVATED = 0.50
_CRITICAL = 0.70


class Input(BaseModel):
    stakeholder_id: str = Field(default="", description="Provider slug or id.")
    baseline_claim_volume: float | None = Field(default=None, description="30-day baseline claim volume.")
    observed_claim_volume: float | None = Field(default=None, description="Observed claim volume in window.")
    business_continuity_runway_days: int | None = Field(
        default=None, description="Days the provider can sustain disruption."
    )


class Output(BaseModel):
    stakeholder_id: str = ""
    disruption_score: float = 0.0
    liquidity_runway_days: int = 0
    impact_tier: str = "none"
    summary: str = ""
    error_type: str = ""
    error_message: str = ""


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _tier(score: float) -> str:
    if score >= _CRITICAL:
        return "critical"
    if score >= _ELEVATED:
        return "elevated"
    if score > 0.0:
        return "moderate"
    return "none"


def assess(inp: Input) -> Output:
    """Deterministic core — disruption_score from the observed claim-volume drop."""
    baseline = inp.baseline_claim_volume
    observed = inp.observed_claim_volume
    if baseline and baseline > 0 and observed is not None:
        drop = _clamp((baseline - observed) / baseline, 0.0, 1.0)
    else:
        drop = 0.0
    score = round(drop, 6)
    runway = int(inp.business_continuity_runway_days or 0)
    tier = _tier(score)
    summary = (
        f"Claim-flow disruption scored {score:.2f} ({tier}); estimated liquidity "
        f"runway {runway} day(s) before payment-continuity escalation."
    )
    return Output(
        stakeholder_id=inp.stakeholder_id,
        disruption_score=score,
        liquidity_runway_days=runway,
        impact_tier=tier,
        summary=summary,
    )


def main(input: Input) -> Output:  # noqa: A002
    try:
        return assess(input)
    except Exception as exc:
        return Output(error_type="ASSESSMENT_FAILED", error_message=str(exc))
