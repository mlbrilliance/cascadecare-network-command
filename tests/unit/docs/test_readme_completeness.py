"""README-completeness gate for Slice 017 — submission inventory.

A Devpost judge confirms project breadth from `README.md`. This gate makes "the
README names every UiPath component" machine-checked instead of trusted: it walks
the real artifact directories (cases, agents, API workflows, BPMN, Flow, App) and
asserts each slug appears in the README, plus frozen lists for the domain assets
that live in `data-model.md` rather than as standalone runtime files (Data Fabric
entities, Context Grounding indexes, Trust Layer pools).

Add an API workflow and forget to document it → this gate goes RED. It also guards
the submission essentials: a linked MIT LICENSE, the Built-with-Coding-Agents
pointer, zero forbidden real-company tokens, and no reference to scripts that do
not exist.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
README = REPO_ROOT / "README.md"
LICENSE = REPO_ROOT / "LICENSE"
CODING_AGENTS = REPO_ROOT / "CODING_AGENTS.md"

# --- Domain assets specified in data-model.md (not standalone runtime files) ---
DATA_FABRIC_ENTITIES = (
    "Provider", "Payer", "Vendor", "Regulator", "Insurer", "Counsel",
    "BAA", "ClaimTelemetry", "RegulatorTemplate",
)
CONTEXT_GROUNDING_INDEXES = ("BAA-corpus", "ClaimTelemetry-corpus")
TRUST_LAYER_POOLS = ("PHI/PII", "content filtering")

# Forbidden real-company tokens (subset; full denylist enforced by /audit-ip-safety).
FORBIDDEN = (
    "zelis", "aetna", "cigna", "unitedhealth", "cotiviti", "optum",
    "change healthcare", "wex ", "rivet", "bcbs",
)

# Scripts the README must not pretend exist (name-honesty guard).
NONEXISTENT_SCRIPTS = ("seed_data_fabric.sh",)


def _readme_text() -> str:
    assert README.is_file(), "README.md missing"
    return README.read_text(encoding="utf-8")


def _slugs(glob_dir: Path, pattern: str, *, exclude: tuple[str, ...] = ()) -> list[str]:
    """Slug = the artifact's own directory name under `glob_dir`."""
    out: list[str] = []
    for match in sorted(glob_dir.glob(pattern)):
        slug = _owning_slug(match, glob_dir)
        if slug and slug not in exclude:
            out.append(slug)
    return out


def _owning_slug(match: Path, base: Path) -> str:
    """First path segment under `base` (the artifact directory name)."""
    rel = match.relative_to(base)
    return rel.parts[0] if rel.parts else ""


# ----- filesystem-driven inventory (single source of truth) -----

def _maestro_cases() -> list[str]:
    base = REPO_ROOT / "maestro_case"
    # Canonical standalone definitions only; clearflow-solution/* are packaged copies.
    return _slugs(base, "*/content/caseplan.json", exclude=("clearflow-solution",))


def _lowcode_agents() -> list[str]:
    base = REPO_ROOT / "agents"
    return _slugs(base, "*/agent.json")


def _coded_agents() -> list[str]:
    base = REPO_ROOT / "agents"
    # agent.py at depth 1 only (`*/agent.py`) — vendored SDK copies live deeper
    # under `<slug>/.venv/.../agent.py` and are excluded by the shallow glob.
    return _slugs(base, "*/agent.py")


def _api_workflows() -> list[str]:
    base = REPO_ROOT / "api_workflows"
    return _slugs(base, "*/main.json")


def _bpmn() -> list[str]:
    base = REPO_ROOT / "maestro_bpmn"
    return _slugs(base, "*/*.bpmn")


def _flows() -> list[str]:
    base = REPO_ROOT / "maestro_flow"
    return _slugs(base, "*/*.flow")


def _apps() -> list[str]:
    base = REPO_ROOT / "apps"
    return _slugs(base, "*/app.json")


ALL_ARTIFACT_GROUPS = {
    "Maestro Case": _maestro_cases,
    "Agent Builder agent": _lowcode_agents,
    "Coded Agent": _coded_agents,
    "API Workflow": _api_workflows,
    "Maestro BPMN": _bpmn,
    "Maestro Flow": _flows,
    "UiPath App": _apps,
}


# ----- counts sanity (catches a glob that silently finds nothing) -----

@pytest.mark.parametrize(
    "group, expected",
    [
        ("Maestro Case", 3),
        ("Agent Builder agent", 4),
        ("Coded Agent", 3),
        ("API Workflow", 14),
        ("Maestro BPMN", 1),
        ("Maestro Flow", 1),
        ("UiPath App", 1),
    ],
)
def test_inventory_counts(group: str, expected: int) -> None:
    found = ALL_ARTIFACT_GROUPS[group]()
    assert len(found) == expected, f"{group}: expected {expected}, found {len(found)}: {found}"


# ----- every real artifact slug is named in the README -----

def test_readme_names_every_artifact() -> None:
    text = _readme_text()
    missing: list[str] = []
    for group, fn in ALL_ARTIFACT_GROUPS.items():
        for slug in fn():
            if slug not in text:
                missing.append(f"[{group}] {slug}")
    assert not missing, "README does not name these artifacts:\n  " + "\n  ".join(missing)


def test_readme_names_data_fabric_entities() -> None:
    text = _readme_text()
    missing = [e for e in DATA_FABRIC_ENTITIES if e not in text]
    assert not missing, f"README missing Data Fabric entities: {missing}"


def test_readme_names_context_grounding_indexes() -> None:
    text = _readme_text()
    missing = [i for i in CONTEXT_GROUNDING_INDEXES if i not in text]
    assert not missing, f"README missing Context Grounding indexes: {missing}"


def test_readme_names_trust_layer_pools() -> None:
    text = _readme_text().lower()
    missing = [p for p in TRUST_LAYER_POOLS if p.lower() not in text]
    assert not missing, f"README missing Trust Layer pools: {missing}"


# ----- submission essentials -----

def test_license_present_and_linked() -> None:
    assert LICENSE.is_file(), "LICENSE file missing"
    assert "MIT" in LICENSE.read_text(encoding="utf-8"), "LICENSE is not MIT"
    text = _readme_text()
    assert "(LICENSE)" in text or "](LICENSE" in text, "README does not link the LICENSE file"


def test_built_with_coding_agents_section() -> None:
    text = _readme_text()
    assert "Built with Coding Agents" in text, "README missing 'Built with Coding Agents' section"
    assert "Claude Code" in text, "README must name the coding agent: Claude Code"
    assert "CODING_AGENTS.md" in text, "README must link CODING_AGENTS.md (bonus evidence)"
    assert CODING_AGENTS.is_file(), "CODING_AGENTS.md (linked bonus evidence) is missing"


def test_no_forbidden_tokens() -> None:
    lower = _readme_text().lower()
    hits = [t for t in FORBIDDEN if t in lower]
    assert not hits, f"README contains forbidden real-company tokens: {hits}"


def test_no_reference_to_nonexistent_scripts() -> None:
    text = _readme_text()
    for script in NONEXISTENT_SCRIPTS:
        if (REPO_ROOT / "scripts" / script).is_file():
            continue  # script exists — reference is fine
        assert script not in text, (
            f"README references scripts/{script}, which does not exist (name-honesty)"
        )
