"""The versioned knowledge layer: load, query, and freshness-filter footgun entries.

Each entry records the platform/CLI version it was proven on and an optional
``resolved_in`` version. When UiPath fixes a footgun, set ``resolved_in`` and the
entry self-deprecates into history instead of misinforming — the freshness risk
becomes a feature (see the requirements doc, KD6).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from importlib.resources import files
from pathlib import Path

_DATA_PACKAGE = "maestro_case_kit.data"
_DATA_FILE = "knowledge.json"


@dataclass(frozen=True)
class KnowledgeEntry:
    """One discovered Maestro Case / Data Fabric / Action Center footgun."""

    id: str
    kind: str
    title: str
    surface: str
    symptom: str
    error_signatures: tuple[str, ...]
    cause: str
    fix: str
    proven_on: str
    severity: str
    references: tuple[str, ...]
    resolved_in: str | None = None

    @property
    def is_active(self) -> bool:
        """True until UiPath ships a fix and ``resolved_in`` is set."""
        return self.resolved_in is None

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "kind": self.kind,
            "title": self.title,
            "surface": self.surface,
            "symptom": self.symptom,
            "error_signatures": list(self.error_signatures),
            "cause": self.cause,
            "fix": self.fix,
            "proven_on": self.proven_on,
            "resolved_in": self.resolved_in,
            "severity": self.severity,
            "references": list(self.references),
        }


def _normalize(text: str) -> str:
    return " ".join(text.casefold().split())


def _read_raw(path: Path | None) -> dict[str, object]:
    if path is None:
        text = files(_DATA_PACKAGE).joinpath(_DATA_FILE).read_text(encoding="utf-8")
    else:
        text = Path(path).read_text(encoding="utf-8")
    return json.loads(text)


def load_entries(path: Path | None = None) -> list[KnowledgeEntry]:
    """Load every knowledge entry from the bundled data file (or a given path)."""
    raw = _read_raw(path)
    items = raw["entries"]
    assert isinstance(items, list)
    entries: list[KnowledgeEntry] = []
    for item in items:
        entries.append(
            KnowledgeEntry(
                id=item["id"],
                kind=item["kind"],
                title=item["title"],
                surface=item["surface"],
                symptom=item["symptom"],
                error_signatures=tuple(item.get("error_signatures", [])),
                cause=item["cause"],
                fix=item["fix"],
                proven_on=item["proven_on"],
                severity=item["severity"],
                references=tuple(item.get("references", [])),
                resolved_in=item.get("resolved_in"),
            )
        )
    return entries


def replace_resolved(entry: KnowledgeEntry, version: str) -> KnowledgeEntry:
    """Return a copy of ``entry`` marked resolved in ``version`` (test/curation helper)."""
    return replace(entry, resolved_in=version)


def active_entries(entries: list[KnowledgeEntry] | None = None) -> list[KnowledgeEntry]:
    """Entries that still bite the current platform (``resolved_in`` unset)."""
    pool = load_entries() if entries is None else entries
    return [e for e in pool if e.is_active]


def find_by_error(
    query: str,
    entries: list[KnowledgeEntry] | None = None,
    include_resolved: bool = False,
) -> list[KnowledgeEntry]:
    """Match a raw error signature against entries' ``error_signatures``."""
    pool = load_entries() if entries is None else entries
    q = _normalize(query)
    if not q:
        return []
    hits: list[KnowledgeEntry] = []
    for e in pool:
        if not include_resolved and not e.is_active:
            continue
        for sig in e.error_signatures:
            ns = _normalize(sig)
            if ns and (q in ns or ns in q):
                hits.append(e)
                break
    return hits


def find(
    query: str,
    entries: list[KnowledgeEntry] | None = None,
    include_resolved: bool = False,
) -> list[KnowledgeEntry]:
    """Error-signature matches first, then a keyword fallback across entry text."""
    pool = load_entries() if entries is None else entries
    q = _normalize(query)
    if not q:
        return []
    candidates = pool if include_resolved else [e for e in pool if e.is_active]
    sig_hits = find_by_error(query, candidates, include_resolved=include_resolved)
    seen = {e.id for e in sig_hits}
    keyword_hits: list[KnowledgeEntry] = []
    for e in candidates:
        if e.id in seen:
            continue
        blob = _normalize(" ".join([e.id, e.title, e.symptom, e.cause, e.fix, e.surface]))
        if q in blob:
            keyword_hits.append(e)
    return sig_hits + keyword_hits
