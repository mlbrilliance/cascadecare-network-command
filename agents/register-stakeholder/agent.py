"""Register Stakeholder & Pull BAA — UiPath Coded Function (mock process).

Deterministic mock for the clearflow-stakeholder-parent "Stakeholder Onboarding"
stage. Completes the narrative step of registering an affected provider customer
and pulling its Business Associate Agreement reference, so the child case walks.

Pure stdlib + pydantic; no LLM, no SDK calls, no randomness, no Date.now() — the
output is a deterministic function of the inputs (timestamps are passed in). IP-safe:
uses only committed fictional provider slugs/names.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

_PROVIDER_NAMES = {
    "northstar": "Northstar Regional Health",
    "alpha": "Alpha Academic Medical Center",
    "beta": "Beta Community Hospital",
    "gamma": "Gamma Health Partners",
    "delta": "Delta Surgical Institute",
    "epsilon": "Epsilon Children's Hospital",
}


class Input(BaseModel):
    """Stakeholder onboarding inputs (all optional; case passes a subset)."""

    stakeholder_id: str = Field(default="", description="Provider slug or Data Fabric id.")
    master_case_id: str = Field(default="", description="Originating master crisis case id.")
    provider_slug: str = Field(default="", description="northstar | alpha | beta | gamma | delta | epsilon")


class Output(BaseModel):
    stakeholder_id: str = ""
    baa_id: str = ""
    onboarding_status: str = "registered"
    summary: str = ""
    error_type: str = ""
    error_message: str = ""


def register(inp: Input) -> Output:
    """Deterministic core — register the stakeholder and resolve its BAA reference."""
    slug = (inp.provider_slug or inp.stakeholder_id or "").strip()
    display = _PROVIDER_NAMES.get(slug, slug or "the affected provider")
    baa_id = f"BAA-{slug.upper()}" if slug else "BAA-UNASSIGNED"
    summary = (
        f"Registered {display} as an affected stakeholder customer and pulled "
        f"its Business Associate Agreement ({baa_id}) for the crisis case."
    )
    return Output(
        stakeholder_id=inp.stakeholder_id or slug,
        baa_id=baa_id,
        onboarding_status="registered",
        summary=summary,
    )


def main(input: Input) -> Output:  # noqa: A002 — UiPath entrypoint signature uses `input`.
    try:
        return register(input)
    except Exception as exc:  # entrypoint must not leak exceptions.
        return Output(error_type="REGISTRATION_FAILED", error_message=str(exc))
