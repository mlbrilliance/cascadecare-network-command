"""Demo pacing helper — auto-complete excess Action Center tasks.

Leaves exactly KEEP_FIDUCIARY Fiduciary tasks and KEEP_OBLIGATION Obligation
Response tasks for the presenter to action live. All others are auto-completed
with realistic alternating decisions so the case network advances cleanly.

Usage (after master crisis has started and tasks have appeared in Action Center):
    uv run python scripts/demo_autocomplete.py

Optional env override:
    DEMO_KEEP_FIDUCIARY=2   (default 2 — 1 to Approve + 1 to Deny)
    DEMO_KEEP_OBLIGATION=2  (default 2 — 1 to File  + 1 to Withdraw)

DEMO FLOW (run this before going live to judges):
    1. Start master crisis run(s) via Demo Driver or:
           uip maestro case process run AC365BA5-C807-4DFC-A009-00F3EA61E497 de7b7c18-d743-4c8c-b555-9bd3b96fe524
       For both Approve AND Deny live: trigger the master crisis TWICE.
    2. Wait ~2 min for grandchild obligation cases to spawn and Action Center
       tasks to appear (watch Orchestrator Jobs or the live dashboard).
    3. Run this script:
           uv run python scripts/demo_autocomplete.py
       Use --dry-run first to preview what will be auto-completed without touching anything:
           uv run python scripts/demo_autocomplete.py --dry-run
    4. You are left with exactly 4 tasks in Action Center:
           Fiduciary  ×2  → Approve one | Deny the other
           Obligation ×2  → File one    | Withdraw the other
       Total live actions: 4. Estimated time on stage: ~60 seconds.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from cascadecare.uipath.auth import UiPathCredentials, get_access_token

FOLDER_KEY = os.getenv("DEMO_FOLDER_KEY", "de7b7c18-d743-4c8c-b555-9bd3b96fe524")
KEEP_FIDUCIARY = int(os.getenv("DEMO_KEEP_FIDUCIARY", "2"))
KEEP_OBLIGATION = int(os.getenv("DEMO_KEEP_OBLIGATION", "2"))

_FIDUCIARY_MARKER = "Fiduciary"
_OBLIGATION_MARKER = "Obligation Response"

Task = dict[str, Any]


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


def classify_tasks(tasks: list[Task]) -> tuple[list[Task], list[Task]]:
    """Split tasks into (fiduciary, obligation) buckets by title substring."""
    fiduciary: list[Task] = []
    obligation: list[Task] = []
    for t in tasks:
        title: str = t.get("Title", "")
        if _FIDUCIARY_MARKER in title:
            fiduciary.append(t)
        elif _OBLIGATION_MARKER in title:
            obligation.append(t)
    return fiduciary, obligation


def partition_tasks(tasks: list[Task], keep: int) -> tuple[list[Task], list[Task]]:
    """Return (auto_complete, keep_for_human). Keeps the last `keep` tasks."""
    if len(tasks) <= keep:
        return [], list(tasks)
    return list(tasks[:-keep]), list(tasks[-keep:])


# ---------------------------------------------------------------------------
# Auto-decision helpers
# ---------------------------------------------------------------------------


def auto_fiduciary_decision(index: int) -> str:
    return "Approve" if index % 2 == 0 else "Deny"


def auto_obligation_disposition(index: int) -> str:
    return "filed" if index % 2 == 0 else "withdrawn"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_fiduciary_payload(decision: str, index: int) -> dict[str, str]:
    return {
        "ReviewerId": "AutoDemo",
        "ReviewerDecision": decision,
        "ReviewerContext": f"Auto-completed for demo pacing (auto-{index}). Decision: {decision}.",
        "ReviewTimestamp": _now_iso(),
    }


def build_obligation_payload(disposition: str, index: int) -> dict[str, str]:
    return {
        "ReviewerId": "AutoDemo",
        "ResponseDisposition": disposition,
        "ResponseNarrative": f"Auto-completed for demo pacing (auto-{index}). Disposition: {disposition}.",
        "FiledTimestamp": _now_iso(),
    }


# ---------------------------------------------------------------------------
# Orchestrator API
# ---------------------------------------------------------------------------


def list_pending_tasks(client: httpx.Client, folder_key: str) -> list[Task]:
    """GET /odata/Tasks — returns all Pending tasks in the folder."""
    resp = client.get(
        "tasks",
        params={"$filter": "Status eq 'Pending'", "$top": 200},
        headers={"X-UIPATH-OrganizationUnitId": folder_key},
    )
    resp.raise_for_status()
    return list(resp.json().get("value", []))


def complete_task(
    client: httpx.Client,
    folder_key: str,
    task_id: int,
    action_data: dict[str, str],
) -> None:
    """POST /odata/Tasks({id})/Complete — mark a task complete with output data."""
    resp = client.post(
        f"tasks({task_id})/UiPath.Server.Configuration.OData.Complete",
        json={"actionData": action_data},
        headers={
            "X-UIPATH-OrganizationUnitId": folder_key,
            "Content-Type": "application/json",
        },
    )
    resp.raise_for_status()


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def _build_http_client(creds: UiPathCredentials, token: str) -> httpx.Client:
    base = f"{creds.tenant_url}/orchestrator_/odata/"
    return httpx.Client(
        base_url=base,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30.0,
    )


def run(dry_run: bool = False) -> None:
    env_path = Path(__file__).parent.parent / ".env"
    creds = UiPathCredentials.from_env(env_path if env_path.exists() else None)
    token = get_access_token(creds, scopes=["OR.Tasks", "OR.Execution", "OR.Cases"])

    with _build_http_client(creds, token) as client:
        tasks = list_pending_tasks(client, FOLDER_KEY)

    if not tasks:
        print("No pending Action Center tasks found. Is the master crisis running?")
        return

    fiduciary, obligation = classify_tasks(tasks)
    fid_auto, fid_keep = partition_tasks(fiduciary, keep=KEEP_FIDUCIARY)
    obl_auto, obl_keep = partition_tasks(obligation, keep=KEEP_OBLIGATION)

    print(f"\n{'DRY RUN — ' if dry_run else ''}Demo Autocomplete")
    print(f"  Fiduciary tasks found   : {len(fiduciary)}  → auto: {len(fid_auto)}, keep: {len(fid_keep)}")
    print(f"  Obligation tasks found  : {len(obligation)} → auto: {len(obl_auto)}, keep: {len(obl_keep)}")

    with _build_http_client(creds, token) as client:
        for i, task in enumerate(fid_auto):
            decision = auto_fiduciary_decision(i)
            payload = build_fiduciary_payload(decision, i)
            if not dry_run:
                complete_task(client, FOLDER_KEY, task["Id"], payload)
            print(f"  [AUTO] Fiduciary #{task['Id']} → {decision}")

        for i, task in enumerate(obl_auto):
            disposition = auto_obligation_disposition(i)
            payload = build_obligation_payload(disposition, i)
            if not dry_run:
                complete_task(client, FOLDER_KEY, task["Id"], payload)
            print(f"  [AUTO] Obligation #{task['Id']} → {disposition}")

    print("\n  ✓ Tasks remaining for YOU to action live:")
    for t in fid_keep:
        print(f"    → Fiduciary  #{t['Id']}  (Approve one, Deny one)")
    for t in obl_keep:
        print(f"    → Obligation #{t['Id']}  (File one, Withdraw one)")
    print()


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    run(dry_run=dry_run)
