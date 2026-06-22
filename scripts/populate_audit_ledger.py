#!/usr/bin/env python3
"""Populate the AuditRecord Data Fabric ledger for one crisis run.

Ops runner around the deterministic core in
``agents/audit-ledger-writer/agent.py``. Composes one immutable, detailed audit
row per dispositioned obligation (canonical scenario bound to the run's master
case reference) and inserts them via the ``uip df records insert`` CLI, skipping
rows whose ``auditRecordId`` already exists (idempotent).

The agent's ``main()`` does the same over ``sdk.entities`` when run in-tenant;
this CLI runner is the credential-light path for populating the ledger right
after a demo run from a workstation that already has ``uip`` authenticated.

Usage:
    uv run python scripts/populate_audit_ledger.py CFCS-67598194 \
        --recorded-at 2026-06-20T03:38:40Z

The entity id is resolved by name (``AuditRecord``) unless ``--entity-id`` is
given. Pass ``--dry-run`` to print the composed rows without inserting.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
AGENT_PY = REPO_ROOT / "agents" / "audit-ledger-writer-langgraph" / "agent.py"


def _load_core() -> Any:
    spec = importlib.util.spec_from_file_location("audit_ledger_core", AGENT_PY)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _uip(*args: str) -> dict[str, Any]:
    res = subprocess.run(["uip", *args], capture_output=True, text=True)
    out = "\n".join(line for line in res.stdout.splitlines() if "Tool factory" not in line)
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return {"Result": "Failure", "Message": out[:400] or res.stderr[:400]}


def _resolve_entity_id(name: str) -> str:
    env = _uip("df", "entities", "list", "--output", "json")
    for ent in env.get("Data", []):
        if ent.get("Name") == name:
            return str(ent.get("Id") or ent.get("Key") or "")
    raise SystemExit(f"entity '{name}' not found — create it first")


def _existing_ids(entity_id: str) -> set[str]:
    env = _uip("df", "records", "list", entity_id, "--output", "json")
    items = (env.get("Data") or {}).get("Items") or []
    ids: set[str] = set()
    for row in items:
        value = row.get("AuditRecordId") or row.get("auditRecordId")
        if value:
            ids.add(str(value))
    return ids


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_ref", help="Master case external id, e.g. CFCS-67598194")
    parser.add_argument("--recorded-at", default="", help="ISO-8601 recording timestamp")
    parser.add_argument("--entity-id", default="", help="AuditRecord entity id (resolved by name if omitted)")
    parser.add_argument("--entity-name", default="AuditRecord")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    core = _load_core()
    rows = core.compose_audit_records(args.case_ref, core.OBLIGATION_CATALOG, args.recorded_at)

    if args.dry_run:
        print(json.dumps(rows, indent=2))
        return 0

    entity_id = args.entity_id or _resolve_entity_id(args.entity_name)
    existing = _existing_ids(entity_id)
    fresh = core.select_new(rows, existing)
    if not fresh:
        print(f"ledger already complete for {args.case_ref}: {len(rows)} rows present, 0 written")
        return 0

    tmp = REPO_ROOT / ".audit_ledger_rows.json"
    tmp.write_text(json.dumps(fresh))
    try:
        env = _uip("df", "records", "insert", entity_id, "--file", str(tmp), "--output", "json")
    finally:
        tmp.unlink(missing_ok=True)

    data = env.get("Data") or {}
    written = data.get("SuccessCount", len(fresh) if env.get("Result") == "Success" else 0)
    failed = data.get("FailureCount", 0)
    skipped = len(rows) - len(fresh)
    print(f"{args.case_ref}: written={written} skipped={skipped} failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
