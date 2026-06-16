"""Contribution gate — validates knowledge entries against the schema and an
optional IP-safety denylist, so curation (not the distribution channel) is the moat.

A contributed entry must be well-formed and free of any caller-supplied forbidden
tokens (e.g. real company names). The denylist is a parameter, not hardcoded, so the
toolkit stays a general public artifact; a host repo passes its own denylist in CI.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

REQUIRED_FIELDS: tuple[str, ...] = (
    "id",
    "kind",
    "title",
    "surface",
    "symptom",
    "cause",
    "fix",
    "proven_on",
    "severity",
)
VALID_SEVERITY: frozenset[str] = frozenset({"high", "medium", "low"})
_LIST_FIELDS: tuple[str, ...] = ("error_signatures", "references")


def _entry_text(entry: dict) -> str:
    parts: list[str] = []
    for value in entry.values():
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, list):
            parts.extend(str(item) for item in value)
    return " ".join(parts).lower()


def validate_entry(entry: dict, denylist: Iterable[str] = ()) -> list[str]:
    """Return a list of problems with one entry; empty means it passes the gate."""
    problems: list[str] = []
    for field in REQUIRED_FIELDS:
        if not entry.get(field):
            problems.append(f"missing or empty required field: {field}")
    severity = entry.get("severity")
    if severity is not None and severity not in VALID_SEVERITY:
        problems.append(f"invalid severity {severity!r} (expected one of {sorted(VALID_SEVERITY)})")
    for field in _LIST_FIELDS:
        if field in entry and not isinstance(entry[field], list):
            problems.append(f"{field} must be a list")
    text = _entry_text(entry)
    entry_id = entry.get("id", "<unknown>")
    for token in denylist:
        if token and token.lower() in text:
            problems.append(f"forbidden token {token!r} in entry {entry_id}")
    return problems


def _coerce_entries(data: object) -> list[dict]:
    if isinstance(data, (str, Path)):
        data = json.loads(Path(data).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        entries = data.get("entries", [])
    else:
        entries = data
    return [e for e in entries if isinstance(e, dict)] if isinstance(entries, list) else []


def validate_knowledge(data: object, denylist: Iterable[str] = ()) -> list[str]:
    """Validate a knowledge collection (path, {"entries": [...]}, or a list)."""
    entries = _coerce_entries(data)
    denylist = tuple(denylist)
    problems: list[str] = []
    ids: list[str] = []
    for entry in entries:
        problems.extend(validate_entry(entry, denylist))
        entry_id = entry.get("id")
        if isinstance(entry_id, str):
            ids.append(entry_id)
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        problems.append(f"duplicate id: {dup}")
    return problems
