"""Claim Flow Anomaly Detector — UiPath Coded Function Agent (Slice 009).

Deterministic core: given one provider's claim telemetry, compute an
``anomaly_score`` in [0, 1] and a ``severity`` band. This is the substance of the
agent and is fully testable without any UiPath auth — the module imports only
stdlib + pydantic at module level, and ``classify_anomaly`` / ``main`` perform no
SDK calls.

The optional first-party-LLM enrichment (``enrich_with_llm``) is a clearly-marked
hook that loads its prompt from ``agents/prompts/claim_flow_anomaly_detector.md``
and calls the UiPath LLM Gateway. It is NOT part of the deterministic path and is
wired/verified at deploy time only. Importing this module must work WITHOUT
UiPath auth, so every UiPath import lives inside a function body.

Output aligns with the ``provider-claim-anomaly`` event contract:
``provider_id``, ``claim_drop_pct``, ``anomaly_score``.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

# ── Severity thresholds (on anomaly_score) ──────────────────────────────────
# critical >= 0.70 deliberately matches the provider-claim-anomaly contract's
# Maestro Trigger filter (anomaly_score >= 0.7).
_LOW = 0.25
_ELEVATED = 0.50
_CRITICAL = 0.70

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "claim_flow_anomaly_detector.md"


class Input(BaseModel):
    """Claim telemetry for a single provider customer."""

    provider_id: str = Field(
        default="",
        description="northstar | alpha | beta | gamma | delta | epsilon",
    )
    claim_drop_pct: float | None = Field(
        default=None,
        description="Observed % drop in claim volume vs 30-day baseline (0-100). "
        "If omitted, derived from baseline/observed volume.",
    )
    baseline_claim_volume: float | None = Field(
        default=None,
        description="30-day baseline claim volume (used if claim_drop_pct absent).",
    )
    observed_claim_volume: float | None = Field(
        default=None,
        description="Observed claim volume in the window (used if claim_drop_pct absent).",
    )
    business_continuity_runway_days: int | None = Field(
        default=None,
        description="Days the provider can sustain disruption before liquidity stress.",
    )


class Output(BaseModel):
    """Per-provider anomaly classification (provider-claim-anomaly contract shape)."""

    provider_id: str = ""
    claim_drop_pct: float = 0.0
    anomaly_score: float = 0.0
    severity: str = "none"
    error_type: str = ""
    error_message: str = ""


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _resolve_drop_pct(inp: Input) -> float:
    """Use explicit claim_drop_pct when given; otherwise derive from volumes.

    Explicit value always wins. Derivation is defensive against a zero/absent
    baseline (no baseline => no establishable drop => 0%).
    """
    if inp.claim_drop_pct is not None:
        return _clamp(float(inp.claim_drop_pct), 0.0, 100.0)

    baseline = inp.baseline_claim_volume
    observed = inp.observed_claim_volume
    if not baseline or baseline <= 0 or observed is None:
        return 0.0

    drop = (baseline - observed) / baseline * 100.0
    return _clamp(drop, 0.0, 100.0)


def _severity_for(score: float) -> str:
    if score >= _CRITICAL:
        return "critical"
    if score >= _ELEVATED:
        return "elevated"
    if score >= _LOW:
        return "low"
    return "none"


def classify_anomaly(inp: Input) -> Output:
    """Deterministic core — no LLM, no SDK. The demo's substance.

    anomaly_score = clamp(claim_drop_pct, 0, 100) / 100, monotonic in the drop.
    """
    drop_pct = _resolve_drop_pct(inp)
    score = round(drop_pct / 100.0, 6)
    return Output(
        provider_id=inp.provider_id,
        claim_drop_pct=drop_pct,
        anomaly_score=score,
        severity=_severity_for(score),
    )


def main(input: Input) -> Output:  # noqa: A002 — UiPath entrypoint signature uses `input`.
    """UiPath Coded Function entrypoint (declared in uipath.json `functions`).

    Errors are returned in the Output fields, never raised, per the Coded
    Function contract.
    """
    try:
        return classify_anomaly(input)
    except Exception as exc:  # entrypoint must not leak exceptions.
        return Output(
            provider_id=input.provider_id,
            error_type="CLASSIFICATION_FAILED",
            error_message=str(exc),
        )


# ── Optional first-party-LLM enrichment (deploy-time only) ──────────────────
# NOT part of the deterministic path. Instantiates the UiPath SDK INSIDE the
# function so importing this module needs no auth. Verified at deploy, not in
# the unit suite.
def enrich_with_llm(output: Output) -> str:
    """Return a two-sentence advisory narrative via the UiPath LLM Gateway.

    Advisory only — never mutates anomaly_score or severity. Loads its system
    prompt from agents/prompts/claim_flow_anomaly_detector.md.
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
                    f"provider_id={output.provider_id} "
                    f"claim_drop_pct={output.claim_drop_pct} "
                    f"anomaly_score={output.anomaly_score} "
                    f"severity={output.severity}. "
                    "Write the two-sentence narrative."
                ),
            },
        ],
    )
    return str(response)
