#!/usr/bin/env python3
"""Shared DB helpers for all memory scripts."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "memory" / "project_memory.db"


def connect() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise SystemExit(
            f"Memory DB not found at {DB_PATH}. Run: python .agent-os/scripts/init_db.py"
        )
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def next_unblocked_tasks(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Return all not_started tasks whose dependencies are all complete."""
    all_tasks = conn.execute("SELECT * FROM task_state").fetchall()
    complete_ids = {r["task_id"] for r in all_tasks if r["status"] == "complete"}
    unblocked = []
    for t in all_tasks:
        if t["status"] != "not_started":
            continue
        deps = [d.strip() for d in (t["dependencies"] or "").split(",") if d.strip()]
        if all(d in complete_ids for d in deps):
            unblocked.append(t)
    return unblocked
