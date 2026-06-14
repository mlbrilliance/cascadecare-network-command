"""Demo pacing helper — auto-complete excess Action Center tasks via the `uip` CLI.

Leaves exactly KEEP_FIDUCIARY Fiduciary tasks and KEEP_OBLIGATION Obligation
Response tasks for the presenter to action live. All others are auto-completed
with realistic alternating decisions so the case network advances cleanly.

WHY THE CLI (not raw OData): Action-Center AppTasks complete through
``POST /tasks/AppTasks/CompleteAppTask`` — the path the ``uip tasks complete
--type AppTask`` verb uses. The earlier httpx version hit the generic
``Tasks(id)/...OData.Complete`` action and ``forms/AppTasks/...`` by hand and got
405s; those were wrong endpoints, not a platform limit. Listing likewise works
with a normal ``uip login`` user token (``--as-admin``) — the "returns 0" problem
was specific to client-credentials auth, which only sees its own tasks.

ORPHANED TASKS: a Pending task whose backing Maestro case instance was stopped
(manual ``jobs stop`` or the hourly case-job-janitor sweep) returns
"This action has been already deleted" on completion. Such tasks are dead husks —
they CANNOT be completed here AND cannot be actioned live in Action Center either.
This script reports them separately; if everything is orphaned you need a FRESH
master run.

Usage (after a master crisis run, once tasks have appeared in Action Center):
    uv run python scripts/demo_autocomplete.py --dry-run   # preview, touches nothing
    uv run python scripts/demo_autocomplete.py             # complete the excess

Env overrides:
    DEMO_ASSIGNEE=you@org.com  (REQUIRED for a real run — the Action-Center user to
                                assign tasks to before completing; usually your login
                                email. AppTask completion fails if the task is unassigned.)
    DEMO_KEEP_FIDUCIARY=2    (default 2 — keep 1 to Approve + 1 to Deny live)
    DEMO_KEEP_OBLIGATION=2   (default 2 — keep 1 to File  + 1 to Withdraw live)
    DEMO_FOLDER_ID=3059530   (numeric Action-Center folder id; unset = all folders)
    DEMO_OBLIGATION_ACTION_FILED / _WITHDRAWN  (outcome names — see note below)
    DEMO_UIP_BIN=uip         (path to the uip binary)

DEMO FLOW (run before going live to judges):
    1. Confirm auth:  uip login status        (staging / hackathon26_042 / DefaultTenant)
    2. Start a FRESH master crisis run:
           uip maestro case process run AC365BA5-C807-4DFC-A009-00F3EA61E497 \
               de7b7c18-d743-4c8c-b555-9bd3b96fe524
       To action BOTH Approve AND Deny live you need 2 Fiduciary tasks → trigger twice.
    3. Wait ~2 min for grandchild obligation cases to spawn and tasks to appear.
    4. Preview, then run (set DEMO_ASSIGNEE to your Action-Center login email):
           uv run python scripts/demo_autocomplete.py --dry-run
           DEMO_ASSIGNEE=you@org.com uv run python scripts/demo_autocomplete.py
    5. You are left with ~4 tasks. Action them LIVE on stage *before* stopping any
       jobs and within 24 h (after which the janitor sweep orphans them).

NOTE on outcome names (verified live 2026-06-14): the Fiduciary app's outcomes are
Approve/Deny. The Obligation app accepts ANY action string — it has no fixed outcome
set — so the File/Withdraw defaults below complete cleanly. Override via
DEMO_OBLIGATION_ACTION_FILED / _WITHDRAWN if desired.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any

KEEP_FIDUCIARY = int(os.getenv("DEMO_KEEP_FIDUCIARY", "2"))
KEEP_OBLIGATION = int(os.getenv("DEMO_KEEP_OBLIGATION", "2"))
UIP_BIN = os.getenv("DEMO_UIP_BIN", "uip")
# Action-Center user to assign tasks to before completing. AppTask completion fails
# ("This action is no longer assigned to you") unless the task is assigned first.
ASSIGNEE = os.getenv("DEMO_ASSIGNEE", "")

_FIDUCIARY_MARKER = "Fiduciary"
_OBLIGATION_MARKER = "Obligation Response"

# Outcome ("--action") names. Fiduciary outcomes are verified; obligation are guesses.
_OBLIGATION_ACTION = {
    "filed": os.getenv("DEMO_OBLIGATION_ACTION_FILED", "File"),
    "withdrawn": os.getenv("DEMO_OBLIGATION_ACTION_WITHDRAWN", "Withdraw"),
}

# Result classifications returned by classify_result().
COMPLETED = "completed"
ORPHANED = "orphaned"
FAILED = "failed"

Task = dict[str, Any]


# ---------------------------------------------------------------------------
# Classification (pure)
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
# Auto-decision helpers (pure)
# ---------------------------------------------------------------------------


def auto_fiduciary_decision(index: int) -> str:
    return "Approve" if index % 2 == 0 else "Deny"


def auto_obligation_disposition(index: int) -> str:
    return "filed" if index % 2 == 0 else "withdrawn"


def fiduciary_action(decision: str) -> str:
    """Outcome button name for the Fiduciary app (== the decision itself)."""
    return decision


def obligation_action(disposition: str) -> str:
    """Outcome button name for the Obligation app (mapped from disposition)."""
    return _OBLIGATION_ACTION.get(disposition, disposition)


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
# uip CLI plumbing (pure helpers + thin IO)
# ---------------------------------------------------------------------------


def parse_task_list(raw: dict[str, Any]) -> list[Task]:
    """Extract the task array from a `uip tasks list --output json` response."""
    data = raw.get("Data")
    if data is None:
        data = raw.get("value", [])
    return list(data or [])


def filter_actionable(tasks: list[Task], folder_id: int | None = None) -> list[Task]:
    """Keep only Pending/Unassigned AppTasks (optionally scoped to a folder)."""
    out: list[Task] = []
    for t in tasks:
        if t.get("Status") not in ("Pending", "Unassigned"):
            continue
        if t.get("Type") not in (None, "AppTask"):
            continue
        if folder_id is not None and t.get("FolderId") != folder_id:
            continue
        out.append(t)
    return out


def build_assign_argv(task: Task, assignee: str) -> list[str]:
    """Build the `uip tasks assign ...` argument vector for one task."""
    return ["tasks", "assign", str(task["Id"]), "--user", assignee]


def build_complete_argv(task: Task, action: str, data: dict[str, str]) -> list[str]:
    """Build the `uip tasks complete ...` argument vector for one AppTask."""
    return [
        "tasks",
        "complete",
        str(task["Id"]),
        "--type",
        "AppTask",
        "--folder-id",
        str(task.get("FolderId", "")),
        "--action",
        action,
        "--data",
        json.dumps(data),
    ]


def classify_result(result: dict[str, Any]) -> str:
    """Map a `uip tasks complete` JSON result to COMPLETED / ORPHANED / FAILED."""
    if result.get("Result") == "Success":
        return COMPLETED
    blob = f"{result.get('Instructions', '')} {result.get('Message', '')}".lower()
    if "already deleted" in blob or "already been completed" in blob:
        return ORPHANED
    return FAILED


def _run_uip(args: list[str]) -> dict[str, Any]:
    """Run `uip <args> --output json` and return the parsed JSON object."""
    proc = subprocess.run(
        [UIP_BIN, *args, "--output", "json"],
        capture_output=True,
        text=True,
    )
    out = proc.stdout.strip()
    try:
        parsed = json.loads(out)
    except json.JSONDecodeError as exc:
        detail = out[:300] or proc.stderr.strip()[:300]
        raise RuntimeError(
            f"`uip {' '.join(args)}` did not return JSON (exit {proc.returncode}): {detail}"
        ) from exc
    if not isinstance(parsed, dict):
        return {"Data": parsed}
    return parsed


def list_actionable_tasks(folder_id: int | None = None) -> list[Task]:
    raw = _run_uip(["tasks", "list", "--as-admin"])
    return filter_actionable(parse_task_list(raw), folder_id)


def assign_task(task: Task, assignee: str) -> bool:
    """Assign one task to `assignee` (best-effort). Required before completing."""
    result = _run_uip(build_assign_argv(task, assignee))
    return result.get("Result") == "Success"


def complete_task(task: Task, action: str, data: dict[str, str]) -> tuple[str, dict[str, Any]]:
    """Complete one AppTask; return (classification, raw_result)."""
    result = _run_uip(build_complete_argv(task, action, data))
    return classify_result(result), result


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def _preflight() -> bool:
    if shutil.which(UIP_BIN) is None and not os.path.exists(UIP_BIN):
        print(f"✗ `{UIP_BIN}` not found on PATH. Install the uip CLI or set DEMO_UIP_BIN.")
        return False
    try:
        status = _run_uip(["login", "status"])
    except RuntimeError as exc:
        print(f"✗ Could not read login status: {exc}")
        return False
    if status.get("Data", {}).get("Status") != "Logged in":
        print("✗ Not logged in. Run `uip login` (staging / hackathon26_042 / DefaultTenant).")
        return False
    d = status["Data"]
    print(f"✓ Logged in: {d.get('Organization')}/{d.get('Tenant')} @ {d.get('BaseUrl')}")
    return True


def _auto_complete(
    bucket: list[Task],
    *,
    is_fiduciary: bool,
    dry_run: bool,
    assignee: str,
) -> dict[str, int]:
    tally = {COMPLETED: 0, ORPHANED: 0, FAILED: 0}
    label = "Fiduciary" if is_fiduciary else "Obligation"
    for i, task in enumerate(bucket):
        if is_fiduciary:
            decision = auto_fiduciary_decision(i)
            action = fiduciary_action(decision)
            payload = build_fiduciary_payload(decision, i)
        else:
            disposition = auto_obligation_disposition(i)
            action = obligation_action(disposition)
            payload = build_obligation_payload(disposition, i)
        if dry_run:
            print(f"  [DRY] {label} #{task['Id']} → {action}")
            continue
        assign_task(task, assignee)  # required: completion fails on an unassigned task
        status, result = complete_task(task, action, payload)
        tally[status] += 1
        glyph = {COMPLETED: "✓", ORPHANED: "⊘", FAILED: "✗"}[status]
        note = "" if status == COMPLETED else f"  ({result.get('Instructions') or result.get('Message')})"
        print(f"  [{glyph}] {label} #{task['Id']} → {action}{note}")
    return tally


def run(dry_run: bool = False) -> None:
    if not _preflight():
        sys.exit(1)

    folder_env = os.getenv("DEMO_FOLDER_ID")
    folder_id = int(folder_env) if folder_env else None

    tasks = list_actionable_tasks(folder_id)
    if not tasks:
        print("No pending Action Center tasks found. Is a master crisis running?")
        return

    fiduciary, obligation = classify_tasks(tasks)
    fid_auto, fid_keep = partition_tasks(fiduciary, keep=KEEP_FIDUCIARY)
    obl_auto, obl_keep = partition_tasks(obligation, keep=KEEP_OBLIGATION)

    print(f"\n{'DRY RUN — ' if dry_run else ''}Demo Autocomplete")
    print(f"  Fiduciary tasks   : {len(fiduciary):2d}  → auto {len(fid_auto)}, keep {len(fid_keep)}")
    print(f"  Obligation tasks  : {len(obligation):2d}  → auto {len(obl_auto)}, keep {len(obl_keep)}")
    print()

    if not dry_run and (fid_auto or obl_auto) and not ASSIGNEE:
        print(
            "✗ DEMO_ASSIGNEE is not set. Completion assigns each task first and fails otherwise.\n"
            "  Set it to your Action-Center login email, e.g.:\n"
            "    DEMO_ASSIGNEE=you@org.com uv run python scripts/demo_autocomplete.py"
        )
        sys.exit(1)

    fid_tally = _auto_complete(fid_auto, is_fiduciary=True, dry_run=dry_run, assignee=ASSIGNEE)
    obl_tally = _auto_complete(obl_auto, is_fiduciary=False, dry_run=dry_run, assignee=ASSIGNEE)

    completed = fid_tally[COMPLETED] + obl_tally[COMPLETED]
    orphaned = fid_tally[ORPHANED] + obl_tally[ORPHANED]
    failed = fid_tally[FAILED] + obl_tally[FAILED]
    attempted = len(fid_auto) + len(obl_auto)

    if not dry_run:
        print(f"\n  Completed {completed} | orphaned {orphaned} | failed {failed} (of {attempted})")
        if orphaned and completed == 0:
            print(
                "\n  ⚠ EVERY task is orphaned — their case instances were stopped.\n"
                "    These are DEAD: they cannot be completed here OR actioned live on stage.\n"
                "    Start a FRESH master crisis run before demoing."
            )
        elif orphaned:
            print(f"  ⚠ {orphaned} orphaned task(s) skipped (dead — backing case instance stopped).")
        if failed:
            print(f"  ✗ {failed} failed for another reason — check the messages above.")

    print("\n  Tasks remaining for YOU to action live:")
    for t in fid_keep:
        print(f"    → Fiduciary  #{t['Id']}  (Approve one, Deny one)")
    for t in obl_keep:
        print(f"    → Obligation #{t['Id']}  (File one, Withdraw one)")
    if (fid_keep or obl_keep) and not dry_run and orphaned and completed == 0:
        print("    (these are likely orphaned too — verify against a fresh run)")
    print()


if __name__ == "__main__":
    run(dry_run="--dry-run" in sys.argv)
