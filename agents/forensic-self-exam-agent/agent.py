"""Forensic Self-Exam Agent — UiPath Coded Function Agent (Slice 009).

Deterministic core: given internal (ClearFlow) and vendor (Nimbus) evidence
flags, produce a routing decision and ClearFlow's vector status. This drives
Reversal 2 ("ClearFlow cleared, Nimbus identified"). It is the substance of the
agent and is fully testable without UiPath auth — module-level imports are
stdlib + pydantic only.

Routing table (authoritative — mirrors the prompt .md):

    clearflow_indicators > 0                  -> vector-hypothesis / unknown
    clearflow == 0, nimbus > 0, not self_victim -> baa-boundary / cleared
    clearflow == 0, nimbus > 0, self_victim     -> baa-boundary / co-victim
    clearflow == 0, nimbus == 0               -> escalate / unknown

Internal evidence dominates: while any ClearFlow indicator remains the status
stays ``unknown`` and the self-victim flag cannot flip it.

The optional first-party-LLM enrichment (``enrich_with_llm``) loads its prompt
from ``agents/prompts/forensic_self_exam_agent.md`` and calls the UiPath LLM
Gateway; it is NOT part of the deterministic path and is verified at deploy time
only. Every UiPath import lives inside a function body.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

ROUTE_VECTOR_HYPOTHESIS = "vector-hypothesis"
ROUTE_BAA_BOUNDARY = "baa-boundary"
ROUTE_ESCALATE = "escalate"

STATUS_UNKNOWN = "unknown"
STATUS_CLEARED = "cleared"
STATUS_CO_VICTIM = "co-victim"

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "forensic_self_exam_agent.md"


class Input(BaseModel):
    """Evidence flags from the internal forensic self-exam."""

    clearflow_indicators: int = Field(
        default=0, description="Count of forensic indicators implicating ClearFlow's own systems."
    )
    nimbus_indicators: int = Field(
        default=0, description="Count of forensic indicators pointing at the Nimbus vendor."
    )
    clearflow_self_victim: bool = Field(
        default=False,
        description="Whether ClearFlow's own systems were also compromised once cleared as vector.",
    )


class Output(BaseModel):
    """Routing decision + ClearFlow vector standing."""

    route_to: str = ROUTE_ESCALATE
    clearflow_vector_status: str = STATUS_UNKNOWN
    error_type: str = ""
    error_message: str = ""


def route_investigation(inp: Input) -> Output:
    """Deterministic routing core — no LLM, no SDK. The demo's substance.

    Negative counts are clamped to zero (a negative count means "no evidence").
    """
    clearflow = max(0, inp.clearflow_indicators)
    nimbus = max(0, inp.nimbus_indicators)

    # Internal evidence dominates — never auto-clear while indicators remain.
    if clearflow > 0:
        return Output(route_to=ROUTE_VECTOR_HYPOTHESIS, clearflow_vector_status=STATUS_UNKNOWN)

    # Cleared internally; evidence points to the vendor -> move to BAA obligations.
    if nimbus > 0:
        status = STATUS_CO_VICTIM if inp.clearflow_self_victim else STATUS_CLEARED
        return Output(route_to=ROUTE_BAA_BOUNDARY, clearflow_vector_status=status)

    # No evidence either way -> escalate for human review / more telemetry.
    return Output(route_to=ROUTE_ESCALATE, clearflow_vector_status=STATUS_UNKNOWN)


def main(input: Input) -> Output:  # noqa: A002 — UiPath entrypoint signature uses `input`.
    """UiPath Coded Function entrypoint (declared in uipath.json `functions`)."""
    try:
        return route_investigation(input)
    except Exception as exc:  # entrypoint must not leak exceptions.
        return Output(error_type="ROUTING_FAILED", error_message=str(exc))


# ── Optional first-party-LLM enrichment (deploy-time only) ──────────────────
# NOT part of the deterministic path. UiPath SDK is instantiated INSIDE the
# function so importing this module needs no auth.
def enrich_with_llm(output: Output) -> str:
    """Return a short plain-language rationale for the routing decision.

    Advisory only — never mutates route_to or clearflow_vector_status. Loads its
    system prompt from agents/prompts/forensic_self_exam_agent.md.
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
                    f"route_to={output.route_to} "
                    f"clearflow_vector_status={output.clearflow_vector_status}. "
                    "Write the short rationale."
                ),
            },
        ],
    )
    return str(response)
