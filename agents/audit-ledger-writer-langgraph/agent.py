"""Audit-Ledger Writer — UiPath LangGraph Coded Agent.

Why a LangGraph Agent (not a Coded Function): a Maestro Case ``type:agent`` task
only wires inputs to an Agent-type process the Studio Web canvas can resolve. A
coded Function is NOT canvas-resolvable, so its inputs (here, the run's
``case_ref``) never get wired and arrive empty — verified live 2026-06-22 (the
Function received ``{}`` and faulted). Re-expressing the writer as a single-node
LangGraph ``StateGraph`` (the forensic-self-exam pattern) makes it an Agent the
canvas resolves, so ``case_ref = metadata.caseId`` is wired and forwarded in-case.

Why this exists: when an obligation grandchild is dispositioned, the in-case
``generate-audit-record`` API workflow records the entry into the case's Action
History — durable, but not a queryable, exportable table. Accreditors (The Joint
Commission, NCQA, ACHC) ask for a *survey-ready* ledger they can filter and
export. This agent persists one immutable, detailed row per obligation into the
``AuditRecord`` Data Fabric entity.

Design: per-instance case variables are transient (the Maestro
``/instances/{id}/global-variables`` blob 404s seconds after completion), so the
ledger's detail is sourced from the canonical, deterministic obligation catalog
(six stakeholders, fixed obligation types) bound to the real run via its master
case reference (e.g. ``CFCS-67598194``). Every row is real scenario data tied to
a real run, never fabricated per-instance values.

The pure core (``compose_audit_records`` / ``select_new`` / ``extract_record_ids``
/ ``run_ledger``) is unchanged and fully testable without UiPath auth; the single
graph node ``write_ledger_node`` is the only auth-gated glue (lazy SDK import).
Writes go through ``sdk.entities`` using the agent's robot identity (no IS
connection). Idempotent: ``auditRecordId`` is keyed on the case reference, so
re-running over the same case writes nothing new. AuditRecord is a tenant/default
DF entity (FolderId all-zeros), so it is resolved WITHOUT a folder_key.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

# CascadeCare-v110 deployment folder (DEMO-RUNBOOK reference table).
DEFAULT_FOLDER_KEY = "de7b7c18-d743-4c8c-b555-9bd3b96fe524"
ENTITY_NAME = "AuditRecord"

# Canonical scenario: six affected stakeholders, each with one dispositioned
# obligation. This is the real demo definition (master caseplan spawn slugs +
# grandchild obligation types), NOT a per-instance read — the source of the
# ledger's audit detail. `disposition` follows the scripted scenario: five
# obligations are filed; epsilon's BAA-disclosure is withdrawn (the compliance
# gap the narrative deliberately shows — see README "Withdraw").
OBLIGATION_CATALOG: dict[str, dict[str, str]] = {
    "northstar": {
        "obligationType": "subpoena-response",
        "jurisdiction": "state-DOI",
        "privilegeFlag": "attorney-client",
        "requestingParty": "regulator",
        "disposition": "filed",
    },
    "alpha": {
        "obligationType": "breach-notification",
        "jurisdiction": "federal",
        "privilegeFlag": "none",
        "requestingParty": "regulator",
        "disposition": "filed",
    },
    "beta": {
        "obligationType": "baa-disclosure",
        "jurisdiction": "contractual",
        "privilegeFlag": "work-product",
        "requestingParty": "payer",
        "disposition": "filed",
    },
    "gamma": {
        "obligationType": "audit-cooperation",
        "jurisdiction": "contractual",
        "privilegeFlag": "none",
        "requestingParty": "payer",
        "disposition": "filed",
    },
    "delta": {
        "obligationType": "subpoena-response",
        "jurisdiction": "state-DOI",
        "privilegeFlag": "attorney-client",
        "requestingParty": "court",
        "disposition": "filed",
    },
    "epsilon": {
        "obligationType": "baa-disclosure",
        "jurisdiction": "contractual",
        "privilegeFlag": "work-product",
        "requestingParty": "payer",
        "disposition": "withdrawn",
    },
}


class Input(BaseModel):
    """Which run to ledger, and the immutable recording timestamp."""

    case_ref: str = Field(
        default="",
        description="Master case external id of the run to ledger (e.g. CFCS-67598194). "
        "Optional with an empty default so an in-case invocation that passes no job "
        "arguments returns data (NO_CASE_REF) instead of faulting on validation.",
    )
    recorded_at: str = Field(
        default="",
        description="ISO-8601 recording timestamp (passed in for determinism — "
        "matches the master case completion time).",
    )
    folder_key: str = Field(
        default=DEFAULT_FOLDER_KEY,
        description="Orchestrator folder hosting the run (GUID).",
    )
    entity_name: str = Field(
        default=ENTITY_NAME,
        description="Data Fabric entity that holds the audit ledger.",
    )
    dry_run: bool = Field(
        default=False,
        description="Compose and report records without inserting anything.",
    )


class Output(BaseModel):
    """Ledger-write report (the agent never raises; errors land here)."""

    case_ref: str = ""
    eligible: int = 0
    written: int = 0
    skipped: int = 0
    record_ids: list[str] = []
    error_type: str = ""
    error_message: str = ""


#: Data Fabric STRING fields cap at 200 chars (verified live 2026-06-20 —
#: a longer value fails the insert), so the narrative stays within that budget;
#: the full detail lives in the structured fields alongside it.
_SUMMARY_MAX = 200


def _summary(stakeholder: str, spec: dict[str, str], case_ref: str, recorded_at: str) -> str:
    """Compose a concise, multi-field human-readable audit narrative (<=200 chars)."""
    text = (
        f"{stakeholder}: {spec['obligationType']} for {spec['requestingParty']} "
        f"({spec['jurisdiction']}). Disposition {spec['disposition']}, privilege "
        f"{spec['privilegeFlag']}. Immutable ledger entry, case {case_ref}."
    )
    return text[:_SUMMARY_MAX]


def compose_audit_records(
    case_ref: str,
    catalog: dict[str, dict[str, str]],
    recorded_at: str,
) -> list[dict[str, Any]]:
    """Build one detailed, immutable audit row per stakeholder (pure).

    Fields are camelCase (underscore names silently drop on Data Fabric insert)
    and exclude the reserved ``id``. ``auditRecordId`` is keyed on the run's
    ``case_ref`` so the same run is idempotent across re-runs.
    """
    records: list[dict[str, Any]] = []
    for stakeholder in sorted(catalog):
        spec = catalog[stakeholder]
        records.append(
            {
                "auditRecordId": f"AUD-{case_ref}-{stakeholder}",
                "caseRef": case_ref,
                "stakeholder": stakeholder,
                "obligationId": f"obl-{stakeholder}-1",
                "obligationType": spec["obligationType"],
                "disposition": spec["disposition"],
                "privilegeFlag": spec["privilegeFlag"],
                "jurisdiction": spec["jurisdiction"],
                "requestingParty": spec["requestingParty"],
                "recordedAt": recorded_at,
                "auditSummary": _summary(stakeholder, spec, case_ref, recorded_at),
            }
        )
    return records


def select_new(
    records: list[dict[str, Any]],
    existing_ids: set[str],
) -> list[dict[str, Any]]:
    """Drop records whose ``auditRecordId`` is already in the ledger (idempotency)."""
    return [r for r in records if r["auditRecordId"] not in existing_ids]


def extract_record_ids(rows: Iterable[Any] | None) -> set[str]:
    """Pull ``auditRecordId`` values from a Data Fabric list response (pure, testable).

    The SDK's ``list_records`` returns an ``EntityRecordsListResponse`` that
    **subclasses ``list``** (iterate it directly — it has no ``.records``/``.value``),
    whose rows are pydantic ``EntityRecord`` objects. Data Fabric also PascalCases
    field names on read (``AuditRecordId``) even though inserts use camelCase
    (``auditRecordId``). Getting either of these wrong reads back zero existing ids
    and silently writes duplicate rows — verified live 2026-06-21. This helper is
    robust to pydantic rows (``model_dump``), plain dicts, and both casings.
    """
    ids: set[str] = set()
    for row in rows or []:
        if hasattr(row, "model_dump"):
            data = row.model_dump()
        elif isinstance(row, dict):
            data = row
        else:
            data = getattr(row, "__dict__", {}) or {}
        value = data.get("AuditRecordId") or data.get("auditRecordId")
        if value:
            ids.add(str(value))
    return ids


def run_ledger(
    inp: Input,
    list_existing_ids: Callable[[], set[str]],
    insert_records: Callable[[list[dict[str, Any]]], None],
    recorded_at: str,
) -> Output:
    """Orchestrate one ledger write over injected list/insert callables (testable)."""
    out = Output(case_ref=inp.case_ref)

    # Guard the empty-input path (an in-case invocation that passes no job args):
    # return data, never fault, and never write empty-ref "AUD--<stakeholder>" garbage.
    if not (inp.case_ref or "").strip():
        out.error_type = "NO_CASE_REF"
        out.error_message = "case_ref not provided — nothing written"
        return out

    records = compose_audit_records(inp.case_ref, OBLIGATION_CATALOG, recorded_at)
    out.eligible = len(records)

    if inp.dry_run:
        return out

    try:
        existing = list_existing_ids()
        fresh = select_new(records, existing)
        out.skipped = len(records) - len(fresh)
        if fresh:
            insert_records(fresh)
        out.written = len(fresh)
        out.record_ids = [r["auditRecordId"] for r in fresh]
    except Exception as exc:  # never raise — a failure becomes data.
        out.error_type = "LEDGER_WRITE_FAILED"
        out.error_message = str(exc)
        out.written = 0
    return out


# ── LangGraph wrapper ──────────────────────────────────────────────────────────
# Single-node graph so the runtime captures the node's full return as the agent
# output (no Annotated reducers / multi-node accumulation to worry about).


class LedgerState(TypedDict, total=False):
    # inputs — the caseplan agent task wires `case_ref = =js:metadata.caseId`.
    case_ref: str
    recorded_at: str
    entity_name: str
    dry_run: bool
    # outputs
    eligible: int
    written: int
    skipped: int
    record_ids: list
    error_type: str
    error_message: str


def write_ledger_node(state: LedgerState) -> dict[str, Any]:
    """The only auth-gated node: resolve the tenant entity, run the pure core.

    Never raises — an empty in-case ``case_ref``, an auth failure, or an insert
    failure all become structured data (NO_CASE_REF / AUTH_FAILED /
    LEDGER_WRITE_FAILED), so the graph (and the case's Closed stage) never fault.
    """
    case_ref = (state.get("case_ref") or "").strip()
    base: dict[str, Any] = {
        "case_ref": state.get("case_ref") or "",
        "eligible": 0, "written": 0, "skipped": 0, "record_ids": [],
        "error_type": "", "error_message": "",
    }

    if not case_ref:
        return {**base, "error_type": "NO_CASE_REF",
                "error_message": "case_ref not provided — nothing written"}

    try:
        from uipath.platform import UiPath  # noqa: PLC0415 — lazy, auth-gated.

        sdk = UiPath()
        entity = sdk.entities.retrieve_by_name(state.get("entity_name") or ENTITY_NAME)
        entity_key = getattr(entity, "key", None) or getattr(entity, "id", "")
    except Exception as exc:
        return {**base, "error_type": "AUTH_FAILED", "error_message": str(exc)}

    def list_existing_ids() -> set[str]:
        return extract_record_ids(sdk.entities.list_records(entity_key, limit=1000))

    def insert_records(rows: list[dict[str, Any]]) -> None:
        sdk.entities.insert_records(entity_key, records=rows)

    recorded_at = state.get("recorded_at") or ""
    inp = Input(case_ref=case_ref, recorded_at=recorded_at, dry_run=bool(state.get("dry_run", False)))
    out = run_ledger(inp, list_existing_ids, insert_records, recorded_at)
    return out.model_dump()


_builder = StateGraph(LedgerState)
_builder.add_node("write_ledger_node", write_ledger_node)
_builder.add_edge(START, "write_ledger_node")
_builder.add_edge("write_ledger_node", END)

graph = _builder.compile()
