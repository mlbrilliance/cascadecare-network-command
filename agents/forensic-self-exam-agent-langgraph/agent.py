"""Forensic Self-Exam Agent — LangGraph version (branch: feat/langgraph-agent).

Same routing logic as the Coded Function original, re-expressed as a LangGraph
StateGraph so UiPath can invoke it via the `type: "agent"` entrypoint pattern.

Graph topology:
    START → clamp_node → route_node ─┬─(escalate)──────────────────► END
                                      └─(vector-hypothesis/baa-boundary)→ enrich_node → END

The LLM enrichment node is skipped on the escalate path (no evidence → no
rationale worth generating). Enrichment failures (auth/offline/Gateway 520/
missing SDK) are caught and surfaced into error_type/error_message — never
swallowed silently, and never allowed to fail the graph or change the route.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

ROUTE_VECTOR_HYPOTHESIS = "vector-hypothesis"
ROUTE_BAA_BOUNDARY = "baa-boundary"
ROUTE_ESCALATE = "escalate"

STATUS_UNKNOWN = "unknown"
STATUS_CLEARED = "cleared"
STATUS_CO_VICTIM = "co-victim"

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "forensic_self_exam_agent.md"


class ForensicState(TypedDict, total=False):
    clearflow_indicators: int
    nimbus_indicators: int
    clearflow_self_victim: bool
    # internal clamped copies
    clearflow_clamped: int
    nimbus_clamped: int
    # outputs
    route_to: str
    clearflow_vector_status: str
    rationale: str
    error_type: str
    error_message: str


# ── Nodes ────────────────────────────────────────────────────────────────────

def clamp_node(state: ForensicState) -> dict:
    return {
        "clearflow_clamped": max(0, state.get("clearflow_indicators", 0)),
        "nimbus_clamped": max(0, state.get("nimbus_indicators", 0)),
    }


def route_node(state: ForensicState) -> dict:
    clearflow = state.get("clearflow_clamped", 0)
    nimbus = state.get("nimbus_clamped", 0)
    self_victim = state.get("clearflow_self_victim", False)

    base = {"rationale": "", "error_type": "", "error_message": ""}

    if clearflow > 0:
        return {**base, "route_to": ROUTE_VECTOR_HYPOTHESIS, "clearflow_vector_status": STATUS_UNKNOWN}

    if nimbus > 0:
        status = STATUS_CO_VICTIM if self_victim else STATUS_CLEARED
        return {**base, "route_to": ROUTE_BAA_BOUNDARY, "clearflow_vector_status": status}

    return {**base, "route_to": ROUTE_ESCALATE, "clearflow_vector_status": STATUS_UNKNOWN}


def enrich_node(state: ForensicState) -> dict:
    """Call the UiPath LLM Gateway for a plain-language rationale. Advisory only.

    On any failure the rationale is left empty and the error is surfaced in
    error_type/error_message (matching the Coded-agent structured-error
    convention). Routing — route_to and clearflow_vector_status set by
    route_node — is authoritative and is never touched here.
    """
    try:
        from uipath.llm_gateway import UiPathOpenAIService  # noqa: PLC0415

        system_prompt = PROMPT_FILE.read_text(encoding="utf-8") if PROMPT_FILE.exists() else (
            "You are a forensic analyst. Explain the routing decision in one sentence."
        )
        service = UiPathOpenAIService()
        rationale = str(service.chat_completions(
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        f"route_to={state.get('route_to')} "
                        f"clearflow_vector_status={state.get('clearflow_vector_status')}. "
                        "Write the short rationale."
                    ),
                },
            ],
        ))
    except Exception as exc:  # advisory enrichment must never fail the graph.
        return {"rationale": "", "error_type": type(exc).__name__, "error_message": str(exc)}

    return {"rationale": rationale, "error_type": "", "error_message": ""}


def _should_enrich(state: ForensicState) -> str:
    if state.get("route_to") == ROUTE_ESCALATE:
        return "skip"
    return "enrich"


# ── Graph assembly ────────────────────────────────────────────────────────────

_builder = StateGraph(ForensicState)
_builder.add_node("clamp_node", clamp_node)
_builder.add_node("route_node", route_node)
_builder.add_node("enrich_node", enrich_node)

_builder.add_edge(START, "clamp_node")
_builder.add_edge("clamp_node", "route_node")
_builder.add_conditional_edges("route_node", _should_enrich, {"enrich": "enrich_node", "skip": END})
_builder.add_edge("enrich_node", END)

graph = _builder.compile()
