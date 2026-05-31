#!/usr/bin/env python3
"""Initialize the agent memory database. Idempotent — safe to re-run."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "memory" / "project_memory.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS session_context (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_date TEXT NOT NULL,
    summary TEXT NOT NULL,
    active_task_id TEXT,
    key_decisions TEXT,
    blockers TEXT,
    next_action TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS task_state (
    task_id TEXT PRIMARY KEY,
    phase TEXT,
    title TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN (
        'not_started', 'in_progress', 'blocked', 'complete', 'frozen', 'skipped'
    )),
    dependencies TEXT,
    acceptance_criteria TEXT,
    risk TEXT,
    completed_at TIMESTAMP,
    notes TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS decision_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT,
    decision TEXT NOT NULL,
    rationale TEXT NOT NULL,
    alternatives_considered TEXT,
    made_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS spec_gate_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    function_name TEXT NOT NULL,
    spec_block TEXT NOT NULL,
    approval_status TEXT CHECK(approval_status IN ('pending','approved','rejected')),
    rejection_reason TEXT,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS checkpoint_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    checkpoint_name TEXT NOT NULL,
    passed INTEGER NOT NULL CHECK(passed IN (0, 1)),
    details TEXT,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS handoff_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    handoff_path TEXT NOT NULL,
    next_task_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS artifact_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT,
    artifact_type TEXT NOT NULL,
    artifact_path TEXT,
    version_hash TEXT,
    metrics TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def init() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    print(f"Memory database initialized at {DB_PATH}")
    print("Tables: session_context, task_state, decision_log, spec_gate_log,")
    print("        checkpoint_log, handoff_log, artifact_versions")


if __name__ == "__main__":
    init()
