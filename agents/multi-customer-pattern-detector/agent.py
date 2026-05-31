"""Multi-Customer Pattern Detector — UiPath Coded Function Agent (Slice 009).

Deterministic core: given a list of per-provider anomaly results, compute the
affected providers, a correlation score, the coincidence likelihood, and the
cascade signal (true iff >= 3 providers are anomalous). The cascade signal is the
Reversal 1 trigger. This is the substance of the agent and is fully testable
without UiPath auth — module-level imports are stdlib + pydantic only.

Output aligns with the ``multi-customer-correlation`` event contract:
``affected_provider_ids``, ``correlation_score``, ``baseline_likelihood_pct``.

The optional first-party-LLM enrichment (``enrich_with_llm``) loads its prompt
from ``agents/prompts/multi_customer_pattern_detector.md`` and calls the UiPath
LLM Gateway; it is NOT part of the deterministic path and is verified at deploy
time only. Every UiPath import lives inside a function body.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

# A provider counts as anomalous at/above this score — matches the
# provider-claim-anomaly contract's Maestro Trigger threshold (>= 0.7).
_ANOMALY_THRESHOLD = 0.70

# Cascade fires once this many distinct providers are anomalous.
_CASCADE_MIN = 3

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "multi_customer_pattern_detector.md"


class ProviderResult(BaseModel):
    """One provider's anomaly result (typically a Claim Flow Anomaly Detector output)."""

    provider_id: str = ""
    anomaly_score: float = 0.0


class Input(BaseModel):
    """Cross-provider correlation request."""

    simulated_day: int = Field(default=0, description="Demo timeline day (0-90).")
    provider_results: list[ProviderResult] = Field(default_factory=list)


class Output(BaseModel):
    """Cross-provider cascade signal (multi-customer-correlation contract shape)."""

    affected_provider_ids: list[str] = Field(default_factory=list)
    correlation_score: float = 0.0
    baseline_likelihood_pct: float = 100.0
    cascade_signal: bool = False
    error_type: str = ""
    error_message: str = ""


# `from __future__ import annotations` stringifies the `list[ProviderResult]`
# annotation on Input. When this module is loaded under a synthetic name (e.g.
# importlib in tests), pydantic cannot auto-resolve the forward ref from the
# caller frame, so resolve it explicitly here.
Input.model_rebuild()


def _dedupe_highest(results: list[ProviderResult]) -> dict[str, float]:
    """Collapse duplicate provider rows, keeping the highest score per provider."""
    best: dict[str, float] = {}
    for r in results:
        score = float(r.anomaly_score)
        if r.provider_id not in best or score > best[r.provider_id]:
            best[r.provider_id] = score
    return best


def _baseline_likelihood_pct(n_affected: int) -> float:
    """Probability (%) that n independent anomalies are coincidence.

    Monotonically decreasing in n; reaches the sub-1% Reversal 1 band at n >= 3.
    """
    return round(100.0 * (0.1**n_affected), 6)


def correlate(inp: Input) -> Output:
    """Deterministic core — no LLM, no SDK. The demo's substance."""
    best = _dedupe_highest(inp.provider_results)
    affected = {pid: score for pid, score in best.items() if score >= _ANOMALY_THRESHOLD}

    affected_ids = sorted(affected)
    n = len(affected_ids)

    correlation = round(sum(affected.values()) / n, 6) if n else 0.0

    return Output(
        affected_provider_ids=affected_ids,
        correlation_score=correlation,
        baseline_likelihood_pct=_baseline_likelihood_pct(n),
        cascade_signal=n >= _CASCADE_MIN,
    )


def main(input: Input) -> Output:  # noqa: A002 — UiPath entrypoint signature uses `input`.
    """UiPath Coded Function entrypoint (declared in uipath.json `functions`)."""
    try:
        return correlate(input)
    except Exception as exc:  # entrypoint must not leak exceptions.
        return Output(error_type="CORRELATION_FAILED", error_message=str(exc))


# ── Optional first-party-LLM enrichment (deploy-time only) ──────────────────
# NOT part of the deterministic path. UiPath SDK is instantiated INSIDE the
# function so importing this module needs no auth.
def enrich_with_llm(output: Output) -> str:
    """Return a one-sentence recommended master CaseGoal shift via the LLM Gateway.

    Advisory only — never mutates cascade_signal or any numeric field. Loads its
    system prompt from agents/prompts/multi_customer_pattern_detector.md.
    """
    from uipath.llm_gateway import UiPathOpenAIService  # noqa: PLC0415 — lazy, auth-gated.

    system_prompt = PROMPT_FILE.read_text(encoding="utf-8")
    service = UiPathOpenAIService()
    response = service.chat_completions(
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"affected_provider_ids={output.affected_provider_ids} "
                    f"correlation_score={output.correlation_score} "
                    f"baseline_likelihood_pct={output.baseline_likelihood_pct} "
                    f"cascade_signal={output.cascade_signal}. "
                    "Write the one-sentence recommended_goal_shift."
                ),
            },
        ],
    )
    return str(response)
