#!/usr/bin/env python3
"""Print everything a fresh agent session needs to resume work.

Run at the START of every session. Paste the output into the agent chat.
"""
from pathlib import Path
from db import connect, next_unblocked_tasks


def main() -> None:
    conn = connect()

    print("=" * 60)
    print("SESSION RESUME CONTEXT")
    print("=" * 60)

    # Most recent handoff document
    handoff = conn.execute(
        "SELECT * FROM handoff_log ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    if handoff:
        path = Path(handoff["handoff_path"])
        print(f"\n## LAST HANDOFF (task {handoff['task_id']} → next {handoff['next_task_id']})")
        if path.exists():
            print(path.read_text())
        else:
            print(f"(handoff file not found at {path} — using DB context only)")

    # Last 3 sessions
    sessions = conn.execute(
        "SELECT * FROM session_context ORDER BY created_at DESC LIMIT 3"
    ).fetchall()
    if sessions:
        print("\n## RECENT SESSIONS")
        for s in sessions:
            print(f"\n[{s['session_date']}] active: {s['active_task_id']}")
            print(f"  Summary: {s['summary']}")
            if s["decisions"] if "decisions" in s.keys() else s["key_decisions"]:
                print(f"  Decisions: {s['key_decisions']}")
            print(f"  Next: {s['next_action']}")

    # In-progress tasks
    in_progress = conn.execute(
        "SELECT * FROM task_state WHERE status = 'in_progress'"
    ).fetchall()
    if in_progress:
        print("\n## IN PROGRESS")
        for t in in_progress:
            print(f"  {t['task_id']} — {t['title']}")

    # Unblocked tasks ready to start
    unblocked = next_unblocked_tasks(conn)
    if unblocked:
        print("\n## READY TO START (dependencies met)")
        for t in unblocked:
            print(f"  {t['task_id']} — {t['title']} (risk: {t['risk'] or 'none'})")

    # Blocked tasks
    blocked = conn.execute(
        "SELECT * FROM task_state WHERE status = 'blocked'"
    ).fetchall()
    if blocked:
        print("\n## BLOCKED")
        for t in blocked:
            print(f"  {t['task_id']} — {t['title']} (deps: {t['dependencies']})")

    # Last 5 decisions
    decisions = conn.execute(
        "SELECT * FROM decision_log ORDER BY made_at DESC LIMIT 5"
    ).fetchall()
    if decisions:
        print("\n## RECENT DECISIONS")
        for d in decisions:
            print(f"  [{d['task_id'] or '-'}] {d['decision']} — {d['rationale']}")

    conn.close()
    print("\n" + "=" * 60)
    print("Paste the above into a fresh agent session to resume.")
    print("Then read CONTEXT.md and any relevant ADRs in docs/adr/.")
    print("=" * 60)


if __name__ == "__main__":
    main()
