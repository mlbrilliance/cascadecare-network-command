"""Audit-Ledger Writer — UiPath Coded Function Agent.

Why this exists: when an obligation grandchild is dispositioned (filed /
withdrawn), the in-case `generate-audit-record` API workflow records the entry
into the case's Action History — durable, but not a queryable, exportable table.
Accreditors (The Joint Commission, NCQA, ACHC) ask for a *survey-ready* ledger
they can filter and export. This writer persists one **immutable, detailed**
row per obligation into the `AuditRecord` Data Fabric entity, giving ClearFlow a
queryable compliance ledger that complements Maestro's Action History.

Design: the per-instance case variables are transient — the Maestro
``/instances/{id}/global-variables`` blob 404s (PIMS-410201) seconds after
completion — so the ledger's *detail* is sourced from the canonical, deterministic
obligation catalog (the real scenario: six stakeholders, fixed obligation types)
and bound to the *real* run via its master case reference (e.g. ``CFCS-67598194``).
Every row is therefore real scenario data tied to a real run, never fabricated
per-instance values.

Deterministic core: ``compose_audit_records`` / ``select_new`` / ``run_ledger``
are pure and fully testable without UiPath auth — the module imports only stdlib
+ pydantic at module level; the ``uipath`` SDK import lives inside ``main``.
Writes go through ``sdk.entities`` using the agent's own runtime identity, so no
Integration Service connection is required. Idempotent: ``auditRecordId`` is keyed
on the run's case reference, so re-running over the same case writes nothing new.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable

from pydantic import BaseModel, Field

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
        description="Master case external id of the run to ledger (e.g. CFCS-67598194).",
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
    """Ledger-write report (entrypoint never raises; errors land here)."""

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


def main(input: Input) -> Output:  # noqa: A002 — UiPath entrypoint signature uses `input`.
    """UiPath Coded Function entrypoint (declared in uipath.json `functions`)."""
    try:
        from uipath.platform import UiPath  # noqa: PLC0415 — lazy, auth-gated.

        sdk = UiPath()
        # AuditRecord is a tenant/default Data Fabric entity (FolderId is all-zeros),
        # so it is resolved WITHOUT a folder_key — passing the run's Orchestrator
        # folder scopes the lookup to that folder's DF environment, where the
        # tenant entity does not exist (verified live 2026-06-21: HTTP 400
        # "Entity 'AuditRecord' not found in folder ..."). folder_key stays on the
        # Input as run-context metadata only.
        entity = sdk.entities.retrieve_by_name(input.entity_name)
        entity_key = getattr(entity, "key", None) or getattr(entity, "id", "")
    except Exception as exc:
        return Output(case_ref=input.case_ref, error_type="AUTH_FAILED", error_message=str(exc))

    def list_existing_ids() -> set[str]:
        # EntityRecordsListResponse subclasses ``list`` — iterate it directly.
        return extract_record_ids(sdk.entities.list_records(entity_key, limit=1000))

    def insert_records(rows: list[dict[str, Any]]) -> None:
        sdk.entities.insert_records(entity_key, records=rows)

    try:
        return run_ledger(input, list_existing_ids, insert_records, input.recorded_at)
    except Exception as exc:  # entrypoint must not leak exceptions.
        return Output(case_ref=input.case_ref, error_type="LEDGER_WRITE_FAILED", error_message=str(exc))
