#!/usr/bin/env python3
"""Log a non-obvious decision so future sessions know the rationale."""
import argparse
from db import connect


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--task_id", default="")
    p.add_argument("--decision", required=True)
    p.add_argument("--rationale", required=True)
    p.add_argument("--alternatives", default="")
    args = p.parse_args()

    conn = connect()
    conn.execute(
        "INSERT INTO decision_log (task_id, decision, rationale, alternatives_considered) "
        "VALUES (?, ?, ?, ?)",
        (args.task_id, args.decision, args.rationale, args.alternatives),
    )
    conn.commit()
    conn.close()
    print(f"Decision logged for {args.task_id or '(no task)'}: {args.decision}")


if __name__ == "__main__":
    main()
