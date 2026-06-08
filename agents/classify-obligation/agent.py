"""Classify Obligation — UiPath Coded Function (mock process).

Deterministic mock for the clearflow-obligation-grandchild "Obligation Intake"
stage. Classifies a per-BAA/per-regulator obligation's type, jurisdiction, and
severity so the grandchild case walks. Pure stdlib + pydantic; no LLM/SDK/randomness.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

# Keyword -> severity. First match wins (checked high to low).
_HIGH = ("subpoena", "breach", "exfiltration", "litigation", "co-defendant")
_MEDIUM = ("audit", "regulator", "doi", "disclosure", "fiduciary")


class Input(BaseModel):
    obligation_type: str = Field(default="", description="e.g. subpoena-response | baa-disclosure | audit-cooperation")
    jurisdiction: str = Field(default="", description="e.g. TN-DOI | federal | contractual")
    baa_id: str = Field(default="", description="Originating BAA reference.")


class Output(BaseModel):
    obligation_type: str = ""
    jurisdiction: str = ""
    severity: str = "low"
    summary: str = ""
    error_type: str = ""
    error_message: str = ""


def _severity(obligation_type: str) -> str:
    text = obligation_type.lower()
    if any(k in text for k in _HIGH):
        return "high"
    if any(k in text for k in _MEDIUM):
        return "medium"
    return "low"


def classify(inp: Input) -> Output:
    """Deterministic core — severity banded from the obligation type keywords."""
    severity = _severity(inp.obligation_type)
    otype = inp.obligation_type or "general-obligation"
    juris = inp.jurisdiction or "contractual"
    summary = (
        f"Classified obligation '{otype}' ({juris}) at {severity} severity"
        + (f" under {inp.baa_id}." if inp.baa_id else ".")
    )
    return Output(obligation_type=otype, jurisdiction=juris, severity=severity, summary=summary)


def main(input: Input) -> Output:  # noqa: A002
    try:
        return classify(input)
    except Exception as exc:
        return Output(error_type="CLASSIFICATION_FAILED", error_message=str(exc))
