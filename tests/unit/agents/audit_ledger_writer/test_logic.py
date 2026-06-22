"""Audit-Ledger Writer — deterministic-core tests (TDD).

Loaded BY PATH so it runs under repo-root `uv run pytest` with no UiPath auth
(every UiPath import lives inside a function body in agent.py).

Covers the pure ledger core: the canonical obligation catalog, the per-run
record composition (camelCase fields, deterministic AUD- ids keyed on the real
master case_ref so re-runs are idempotent), the new-record selection filter, and
the never-raise orchestration over injected list/insert callables.

Why this exists: each dispositioned obligation grandchild must leave an
immutable, queryable row in the AuditRecord Data Fabric entity — a survey-ready
compliance ledger that complements Maestro's Action History. The per-instance
case variables are transient (global-variables blob 404s after completion), so
the ledger's detail is sourced from the canonical deterministic scenario bound
to the real run's case_ref.

The deterministic core lives in the deployed Coded Agent at
``agents/audit-ledger-writer/agent.py`` (single source of truth — the ops runner
``scripts/populate_audit_ledger.py`` loads the same module by path).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from types import ModuleType

REPO_ROOT = Path(__file__).parents[4]
AGENT_PY = REPO_ROOT / "agents" / "audit-ledger-writer-langgraph" / "agent.py"

CASE_REF = "CFCS-67598194"
RECORDED_AT = "2026-06-20T03:38:40Z"

# Fields every immutable audit row must carry (camelCase; no reserved `id`).
EXPECTED_FIELDS = {
    "auditRecordId",
    "caseRef",
    "stakeholder",
    "obligationType",
    "disposition",
    "privilegeFlag",
    "jurisdiction",
    "requestingParty",
    "recordedAt",
    "auditSummary",
}


def _load_agent() -> ModuleType:
    spec = importlib.util.spec_from_file_location("audit_ledger_under_test", AGENT_PY)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def agent() -> ModuleType:
    assert AGENT_PY.exists(), f"agent.py not found at {AGENT_PY}"
    return _load_agent()


class TestImportsWithoutAuth:
    def test_module_imports_without_uipath_auth(self, agent: ModuleType) -> None:
        for sym in ("OBLIGATION_CATALOG", "compose_audit_records", "select_new",
                    "run_ledger", "extract_record_ids", "Input", "Output", "graph"):
            assert hasattr(agent, sym), f"missing {sym}"


class TestCatalog:
    def test_six_canonical_stakeholders(self, agent: ModuleType) -> None:
        assert set(agent.OBLIGATION_CATALOG) == {
            "northstar", "alpha", "beta", "gamma", "delta", "epsilon",
        }

    def test_catalog_uses_only_known_obligation_types(self, agent: ModuleType) -> None:
        allowed = {"subpoena-response", "breach-notification",
                   "baa-disclosure", "audit-cooperation"}
        for slug, spec in agent.OBLIGATION_CATALOG.items():
            assert spec["obligationType"] in allowed, slug


class TestComposeAuditRecords:
    def test_one_detailed_record_per_stakeholder(self, agent: ModuleType) -> None:
        recs = agent.compose_audit_records(CASE_REF, agent.OBLIGATION_CATALOG, RECORDED_AT)
        assert len(recs) == 6

    def test_records_have_all_fields_camelcase(self, agent: ModuleType) -> None:
        recs = agent.compose_audit_records(CASE_REF, agent.OBLIGATION_CATALOG, RECORDED_AT)
        for r in recs:
            assert EXPECTED_FIELDS <= set(r), set(r)
            assert "id" not in r  # reserved field drops on insert
            assert all("_" not in k for k in r)  # underscores drop on insert

    def test_audit_ids_unique_and_run_scoped(self, agent: ModuleType) -> None:
        recs = agent.compose_audit_records(CASE_REF, agent.OBLIGATION_CATALOG, RECORDED_AT)
        ids = [r["auditRecordId"] for r in recs]
        assert len(set(ids)) == 6
        assert all(r["auditRecordId"].startswith(f"AUD-{CASE_REF}-") for r in recs)
        assert all(r["caseRef"] == CASE_REF for r in recs)

    def test_summary_is_detailed_multifield(self, agent: ModuleType) -> None:
        recs = agent.compose_audit_records(CASE_REF, agent.OBLIGATION_CATALOG, RECORDED_AT)
        for r in recs:
            s = r["auditSummary"]
            assert len(s) > 40
            # Data Fabric STRING fields cap at 200 chars — over-length fails insert.
            assert len(s) <= 200
            assert r["disposition"] in s
            assert r["obligationType"] in s

    def test_deterministic(self, agent: ModuleType) -> None:
        a = agent.compose_audit_records(CASE_REF, agent.OBLIGATION_CATALOG, RECORDED_AT)
        b = agent.compose_audit_records(CASE_REF, agent.OBLIGATION_CATALOG, RECORDED_AT)
        assert a == b


class _FakeRecord:
    """Stand-in for a pydantic EntityRecord (has model_dump)."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    def model_dump(self) -> dict[str, Any]:
        return self._data


class TestExtractRecordIds:
    """Idempotency depends on reading existing ids back from the DF list response.

    The live SDK returns an ``EntityRecordsListResponse`` (a ``list`` subclass) of
    pydantic ``EntityRecord`` rows, and Data Fabric PascalCases field names on read
    (``AuditRecordId``) even though we insert camelCase (``auditRecordId``). A
    regression here silently writes duplicate rows (verified live 2026-06-21).
    """

    def test_reads_pascalcase_from_dicts(self, agent: ModuleType) -> None:
        rows = [{"AuditRecordId": "AUD-x-alpha"}, {"AuditRecordId": "AUD-x-beta"}]
        assert agent.extract_record_ids(rows) == {"AUD-x-alpha", "AUD-x-beta"}

    def test_reads_camelcase_from_dicts(self, agent: ModuleType) -> None:
        rows = [{"auditRecordId": "AUD-x-alpha"}]
        assert agent.extract_record_ids(rows) == {"AUD-x-alpha"}

    def test_reads_from_pydantic_like_rows(self, agent: ModuleType) -> None:
        rows = [_FakeRecord({"AuditRecordId": "AUD-x-alpha", "CaseRef": "x"}),
                _FakeRecord({"AuditRecordId": "AUD-x-beta"})]
        assert agent.extract_record_ids(rows) == {"AUD-x-alpha", "AUD-x-beta"}

    def test_empty_and_missing_field(self, agent: ModuleType) -> None:
        assert agent.extract_record_ids([]) == set()
        assert agent.extract_record_ids(None) == set()
        assert agent.extract_record_ids([{"CaseRef": "x"}]) == set()


class TestSelectNew:
    def test_filters_already_written_ids(self, agent: ModuleType) -> None:
        recs = agent.compose_audit_records(CASE_REF, agent.OBLIGATION_CATALOG, RECORDED_AT)
        existing = {recs[0]["auditRecordId"], recs[1]["auditRecordId"]}
        fresh = agent.select_new(recs, existing)
        assert len(fresh) == 4
        assert all(r["auditRecordId"] not in existing for r in fresh)

    def test_empty_existing_keeps_all(self, agent: ModuleType) -> None:
        recs = agent.compose_audit_records(CASE_REF, agent.OBLIGATION_CATALOG, RECORDED_AT)
        assert agent.select_new(recs, set()) == recs


class TestRunLedger:
    def test_writes_fresh_records(self, agent: ModuleType) -> None:
        inserted: list[dict[str, Any]] = []
        inp = agent.Input(case_ref=CASE_REF, recorded_at=RECORDED_AT)
        out = agent.run_ledger(
            inp,
            list_existing_ids=lambda: set(),
            insert_records=lambda rows: inserted.extend(rows),
            recorded_at=RECORDED_AT,
        )
        assert out.written == 6
        assert out.skipped == 0
        assert len(inserted) == 6
        assert out.error_type == ""

    def test_idempotent_second_run_writes_zero(self, agent: ModuleType) -> None:
        recs = agent.compose_audit_records(CASE_REF, agent.OBLIGATION_CATALOG, RECORDED_AT)
        all_ids = {r["auditRecordId"] for r in recs}
        inserted: list[dict[str, Any]] = []
        inp = agent.Input(case_ref=CASE_REF, recorded_at=RECORDED_AT)
        out = agent.run_ledger(
            inp,
            list_existing_ids=lambda: all_ids,
            insert_records=lambda rows: inserted.extend(rows),
            recorded_at=RECORDED_AT,
        )
        assert out.written == 0
        assert out.skipped == 6
        assert inserted == []

    def test_dry_run_inserts_nothing(self, agent: ModuleType) -> None:
        inserted: list[dict[str, Any]] = []
        inp = agent.Input(case_ref=CASE_REF, recorded_at=RECORDED_AT, dry_run=True)
        out = agent.run_ledger(
            inp,
            list_existing_ids=lambda: set(),
            insert_records=lambda rows: inserted.extend(rows),
            recorded_at=RECORDED_AT,
        )
        assert out.written == 0
        assert out.eligible == 6
        assert inserted == []

    def test_insert_failure_surfaces_error_not_raise(self, agent: ModuleType) -> None:
        def boom(_rows: list[dict[str, Any]]) -> None:
            raise RuntimeError("entity insert 500")

        inp = agent.Input(case_ref=CASE_REF, recorded_at=RECORDED_AT)
        out = agent.run_ledger(
            inp,
            list_existing_ids=lambda: set(),
            insert_records=boom,
            recorded_at=RECORDED_AT,
        )
        assert out.error_type == "LEDGER_WRITE_FAILED"
        assert "entity insert 500" in out.error_message
        assert out.written == 0

    def test_list_failure_surfaces_error_not_raise(self, agent: ModuleType) -> None:
        def boom() -> set[str]:
            raise RuntimeError("entity list 503")

        inp = agent.Input(case_ref=CASE_REF, recorded_at=RECORDED_AT)
        out = agent.run_ledger(
            inp,
            list_existing_ids=boom,
            insert_records=lambda rows: None,
            recorded_at=RECORDED_AT,
        )
        assert out.error_type == "LEDGER_WRITE_FAILED"
        assert "entity list 503" in out.error_message

    def test_empty_case_ref_writes_nothing_not_raise(self, agent: ModuleType) -> None:
        # In-case: a type:agent invocation of a coded Function does not pass
        # data.inputs[] as job args, so case_ref can arrive empty. The agent must
        # return data (NO_CASE_REF), never fault, and never write empty-ref garbage.
        inserted: list[dict[str, Any]] = []
        inp = agent.Input(case_ref="", recorded_at=RECORDED_AT)
        out = agent.run_ledger(
            inp,
            list_existing_ids=lambda: set(),
            insert_records=lambda rows: inserted.extend(rows),
            recorded_at=RECORDED_AT,
        )
        assert out.error_type == "NO_CASE_REF"
        assert out.written == 0
        assert out.eligible == 0
        assert inserted == []


class TestInput:
    def test_case_ref_optional_no_validation_error(self, agent: ModuleType) -> None:
        # case_ref defaults to "" so an empty in-case input dict does not raise a
        # pydantic validation error (which would fault the job, not return data).
        assert agent.Input().case_ref == ""
