#!/usr/bin/env python3
"""Save a session summary to memory. Call at the end of every working session."""
import argparse
from datetime import date
from db import connect


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--summary", required=True)
    p.add_argument("--active_task", default="")
    p.add_argument("--decisions", default="")
    p.add_argument("--blockers", default="none")
    p.add_argument("--next_action", default="")
    args = p.parse_args()

    conn = connect()
    conn.execute(
        "INSERT INTO session_context "
        "(session_date, summary, active_task_id, key_decisions, blockers, next_action) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (str(date.today()), args.summary, args.active_task,
         args.decisions, args.blockers, args.next_action),
    )
    conn.commit()
    conn.close()
    print(f"Session saved ({date.today()}).")
    print(f"  Active task: {args.active_task}")
    print(f"  Next: {args.next_action}")


if __name__ == "__main__":
    main()
