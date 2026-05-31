"""Evidence-completeness gate for Slice 016 — coding-agent authorship.

The AgentHack coding-agent bonus needs three things documented: (a) which tool
(Claude Code), (b) how it contributed, (c) verifiable evidence. This gate asserts
the canonical reference and per-type evidence pages exist, name the tool, carry
the (a)/(b)/(c) triad, and cover every UiPath artifact group — so "every artifact
has an evidence channel" is machine-checked, not assumed.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]

CODING_AGENTS = REPO_ROOT / "CODING_AGENTS.md"
USAGE = REPO_ROOT / "CLAUDE_CODE_USAGE.md"
EVIDENCE_DIR = REPO_ROOT / "docs" / "coding-agents"

PER_TYPE_PAGES = [
    "cases.md",
    "agents-lowcode.md",
    "agents-coded.md",
    "api-workflows.md",
    "bpmn.md",
    "flow.md",
    "apps.md",
    "README.md",
]

# Forbidden real-company tokens (subset; full denylist in /audit-ip-safety).
FORBIDDEN = (
    "zelis", "aetna", "cigna", "unitedhealth", "cotiviti", "optum",
    "change healthcare", "wex ", "rivet",
)


def test_canonical_reference_exists() -> None:
    assert CODING_AGENTS.is_file(), "CODING_AGENTS.md missing (Channel 1)"
    assert USAGE.is_file(), "CLAUDE_CODE_USAGE.md missing (Devpost bonus doc)"


def test_names_the_tool_and_bonus_triad() -> None:
    text = CODING_AGENTS.read_text().lower()
    assert "claude code" in text, "must name the tool: Claude Code"
    # (a) tool, (b) contribution, (c) evidence — the bonus triad
    assert "evidence" in text and "contribut" in text, "missing the (b)/(c) triad framing"


def test_covers_every_artifact_group() -> None:
    text = CODING_AGENTS.read_text().lower()
    for group in ("case", "agent builder", "coded agent", "api workflow", "bpmn", "flow", "app"):
        assert group in text, f"CODING_AGENTS.md omits the {group!r} artifact group"
    # the headline artifact count must be stated
    assert "27" in CODING_AGENTS.read_text(), "must state the 27-artifact total"


@pytest.mark.parametrize("page", PER_TYPE_PAGES)
def test_per_type_pages_exist(page: str) -> None:
    assert (EVIDENCE_DIR / page).is_file(), f"docs/coding-agents/{page} missing (Channel 2)"


def test_scaffold_channels_present() -> None:
    assert (REPO_ROOT / "docs" / "prompt-logs" / "README.md").is_file(), "prompt-logs channel missing"
    assert (EVIDENCE_DIR / "screenshots" / "README.md").is_file(), "screenshots channel missing"


@pytest.mark.parametrize(
    "doc",
    [CODING_AGENTS, USAGE, *[EVIDENCE_DIR / p for p in PER_TYPE_PAGES]],
)
def test_evidence_docs_ip_safe(doc: Path) -> None:
    if not doc.is_file():
        pytest.skip(f"{doc} not yet authored")
    lower = doc.read_text().lower()
    hits = [t for t in FORBIDDEN if t in lower]
    assert not hits, f"{doc.name}: forbidden IP token(s) {hits}"
