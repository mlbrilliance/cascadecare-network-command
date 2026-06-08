"""Generate Audit Record — UiPath Coded Function (mock process).

Deterministic mock for the clearflow-obligation-grandchild "Obligation Response"
stage. Produces an immutable audit-record reference for a filed obligation
response so the grandchild case closes. Pure stdlib + pydantic; no LLM/SDK/randomness.
The timestamp is an INPUT (never generated) to keep the output deterministic.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Input(BaseModel):
    obligation_id: str = Field(default="", description="Obligation/response identifier.")
    disposition: str = Field(default="", description="e.g. filed | acknowledged | escalated")
    recorded_at: str = Field(default="", description="Caller-supplied timestamp (no Date.now()).")


class Output(BaseModel):
    audit_record_id: str = ""
    recorded_at: str = ""
    disposition: str = "recorded"
    summary: str = ""
    error_type: str = ""
    error_message: str = ""


def generate(inp: Input) -> Output:
    """Deterministic core — audit id derived from the obligation id; timestamp echoed."""
    oid = (inp.obligation_id or "UNASSIGNED").strip()
    audit_record_id = f"AUD-{oid.upper()}"
    disposition = inp.disposition or "recorded"
    summary = (
        f"Generated immutable audit record {audit_record_id} for obligation "
        f"'{oid}' (disposition: {disposition})."
    )
    return Output(
        audit_record_id=audit_record_id,
        recorded_at=inp.recorded_at,
        disposition=disposition,
        summary=summary,
    )


def main(input: Input) -> Output:  # noqa: A002
    try:
        return generate(input)
    except Exception as exc:
        return Output(error_type="AUDIT_FAILED", error_message=str(exc))
