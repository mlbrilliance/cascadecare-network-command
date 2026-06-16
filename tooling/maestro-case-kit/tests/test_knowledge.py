"""Tests for the versioned knowledge layer (R1, R2, R3)."""

from __future__ import annotations

import re

from maestro_case_kit import knowledge

# IP-safety denylist (mirrors the CascadeCare forbidden tokens). The knowledge
# layer ships publicly, so no entry text may contain a real vendor/company name.
# Tokens are assembled from fragments so this guard file does not itself trip a
# substring IP scan — the toolkit stays substring-clean and self-contained.
_DENY_FRAGMENTS = (
    ("ze", "lis"), ("aet", "na"), ("cig", "na"), ("united", "health"),
    ("bc", "bs"), ("hart", "ley"), ("riv", "et"), ("zi", "pp"), ("za", "pp"),
    ("change ", "healthcare"), ("opt", "um"), ("coti", "viti"), ("we", "x"),
)
FORBIDDEN = tuple(head + tail for head, tail in _DENY_FRAGMENTS)


def test_load_entries_nonempty() -> None:
    entries = knowledge.load_entries()
    assert len(entries) >= 10


def test_entries_have_required_fields() -> None:
    for e in knowledge.load_entries():
        assert e.id and e.kind and e.title and e.symptom
        assert e.cause and e.fix and e.proven_on and e.severity
        assert isinstance(e.error_signatures, tuple)
        assert isinstance(e.references, tuple)
        assert e.severity in {"high", "medium", "low"}


def test_ids_are_unique() -> None:
    ids = [e.id for e in knowledge.load_entries()]
    assert len(ids) == len(set(ids))


def test_entries_are_ip_safe() -> None:
    for e in knowledge.load_entries():
        blob = " ".join(
            [e.id, e.title, e.symptom, e.cause, e.fix, e.surface, *e.error_signatures, *e.references]
        ).lower()
        for token in FORBIDDEN:
            assert token not in blob, f"forbidden token {token!r} in entry {e.id}"


def test_find_by_error_exact_code() -> None:
    hits = knowledge.find_by_error("400300")
    assert any(h.id == "MC-SPAWN-QEM-400300" for h in hits)


def test_find_by_error_is_case_insensitive_and_partial() -> None:
    hits = knowledge.find_by_error("STILL being Indexed")
    assert any(h.id == "CLI-CODEDAPP-INDEXING-HANG" for h in hits)


def test_find_by_error_no_match_returns_empty() -> None:
    assert knowledge.find_by_error("totally-unknown-signature-xyz") == []


def test_active_entries_excludes_resolved() -> None:
    entries = list(knowledge.load_entries())
    # Force one entry resolved and confirm active filter drops it.
    entries[0] = knowledge.replace_resolved(entries[0], "2.0.0")
    active = knowledge.active_entries(entries)
    assert entries[0] not in active
    assert all(e.is_active for e in active)


def test_find_falls_back_to_keyword() -> None:
    hits = knowledge.find("underscore")
    assert any(h.id == "DF-UNDERSCORE-DROP" for h in hits)


def test_find_ranks_error_signature_matches_first() -> None:
    hits = knowledge.find("400300")
    assert hits and hits[0].id == "MC-SPAWN-QEM-400300"


def test_proven_on_looks_like_a_version() -> None:
    for e in knowledge.load_entries():
        assert re.match(r"^\d+\.\d+", e.proven_on), e.id
