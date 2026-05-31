#!/usr/bin/env python3
"""Record a checkpoint result. A failed checkpoint exits non-zero to halt autopilot."""
import argparse
import sys
from db import connect


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--task_id", required=True)
    p.add_argument("--checkpoint_name", required=True)
    p.add_argument("--passed", type=int, choices=[0, 1], required=True)
    p.add_argument("--details", default="")
    args = p.parse_args()

    conn = connect()
    conn.execute(
        "INSERT INTO checkpoint_log (task_id, checkpoint_name, passed, details) "
        "VALUES (?, ?, ?, ?)",
        (args.task_id, args.checkpoint_name, args.passed, args.details),
    )
    conn.commit()
    conn.close()

    status = "PASSED" if args.passed else "FAILED"
    print(f"[{status}] {args.task_id} / {args.checkpoint_name}: {args.details}")

    if not args.passed:
        print("\nCHECKPOINT FAILED — autopilot halted.")
        print("Resolve the failure or say 'override' before proceeding.")
        sys.exit(2)


if __name__ == "__main__":
    main()
