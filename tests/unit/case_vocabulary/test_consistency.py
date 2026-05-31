"""
Candidate 3 — Case Vocabulary Consistency Tests

Verifies that every variable name, stage ID, and task ID referenced in
any caseplan.json file under maestro_case/**/content/caseplan.json
resolves against specs/003-uipath-native/case-vocabulary.yaml.

Design decisions:
- Fails loudly when case-vocabulary.yaml does not exist (guards Slice 005 prep).
- Skips gracefully when a caseplan.json file does not yet exist (parent and
  grandchild files won't exist until Slice 010; the test accumulates coverage
  incrementally as new case definitions are authored, rather than blocking CI).
- Collects all violations before reporting, so a single run shows the full
  picture rather than stopping at the first failure.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).parents[3]
VOCAB_PATH = REPO_ROOT / "specs" / "003-uipath-native" / "case-vocabulary.yaml"
MAESTRO_ROOT = REPO_ROOT / "maestro_case"

# The three canonical caseplan.json paths the project will eventually have.
CANONICAL_CASEPLANS = {
    "master": MAESTRO_ROOT / "clearflow-master-crisis" / "content" / "caseplan.json",
    "stakeholder_parent": MAESTRO_ROOT / "clearflow-stakeholder-parent" / "content" / "caseplan.json",
    "obligation_grandchild": MAESTRO_ROOT / "clearflow-obligation-grandchild" / "content" / "caseplan.json",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_vocabulary() -> dict[str, Any]:
    if not VOCAB_PATH.exists():
        pytest.fail(
            f"case-vocabulary.yaml not found — create it at {VOCAB_PATH.relative_to(REPO_ROOT)}\n"
            "Run: uv run pytest tests/unit/case_vocabulary/ -v to verify after creating."
        )
    return yaml.safe_load(VOCAB_PATH.read_text())


def load_caseplan(path: Path) -> dict[str, Any] | None:
    """Return parsed caseplan or None if file not yet authored."""
    if not path.exists():
        return None
    return json.loads(path.read_text())


def collect_variable_names(caseplan: dict[str, Any]) -> set[str]:
    variables = caseplan.get("variables", [])
    if isinstance(variables, dict):
        # V20 shape: {"inputs": [...], "outputs": [...], "inputOutputs": [...]}
        return {
            v["name"]
            for bucket in ("inputs", "outputs", "inputOutputs")
            for v in variables.get(bucket, [])
        }
    # Legacy flat-array shape (pre-V20 caseplans)
    return {v["name"] for v in variables}


def collect_stage_ids(caseplan: dict[str, Any]) -> set[str]:
    return {
        n["id"]
        for n in caseplan.get("nodes", [])
        if "Stage" in n.get("type", "")
    }


def collect_task_ids(caseplan: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for n in caseplan.get("nodes", []):
        if "Stage" not in n.get("type", ""):
            continue
        for row in n.get("data", {}).get("tasks", []):
            for task in (row if isinstance(row, list) else [row]):
                ids.add(task["id"])
    return ids


def vocab_variable_names(vocab: dict[str, Any], case_key: str) -> set[str]:
    """Return the set of variable names registered for a given case_key."""
    return {v["name"] for v in vocab.get("variables", {}).get(case_key, [])}


def vocab_stage_ids(vocab: dict[str, Any], case_key: str) -> set[str]:
    entries = vocab.get("stages", {}).get(case_key, []) or []
    return {s["id"] for s in entries}


def vocab_task_ids(vocab: dict[str, Any], case_key: str) -> set[str]:
    entries = vocab.get("tasks", {}).get(case_key, []) or []
    return {t["id"] for t in entries}


def vocab_stakeholder_ids(vocab: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for group in vocab.get("stakeholders", {}).values():
        for s in group:
            ids.add(s["id"])
    return ids


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestVocabularyFileExists:
    def test_vocabulary_yaml_is_present(self) -> None:
        """The vocabulary file must exist before any Slice 005+ work proceeds."""
        assert VOCAB_PATH.exists(), (
            f"case-vocabulary.yaml not found at {VOCAB_PATH}. "
            "Create it before continuing."
        )

    def test_vocabulary_yaml_is_valid_yaml(self) -> None:
        vocab = load_vocabulary()
        assert isinstance(vocab, dict), "case-vocabulary.yaml must be a YAML mapping at the top level."

    def test_vocabulary_has_required_top_level_keys(self) -> None:
        vocab = load_vocabulary()
        required = {"schema_version", "variables", "stages", "tasks", "agents", "stakeholders", "event_types"}
        missing = required - set(vocab.keys())
        assert not missing, f"case-vocabulary.yaml is missing required keys: {sorted(missing)}"


class TestMasterCaseplan:
    """Validates the master caseplan.json (must exist from Slice 003)."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.vocab = load_vocabulary()
        self.caseplan = load_caseplan(CANONICAL_CASEPLANS["master"])
        if self.caseplan is None:
            pytest.fail("clearflow-master-crisis/content/caseplan.json is missing — required from Slice 003.")

    def test_all_variable_names_in_vocabulary(self) -> None:
        actual = collect_variable_names(self.caseplan)
        registered = vocab_variable_names(self.vocab, "master")
        unregistered = actual - registered
        assert not unregistered, (
            f"Master caseplan.json has variable names not in vocabulary (master section): "
            f"{sorted(unregistered)}\nAdd them to case-vocabulary.yaml → variables.master"
        )

    def test_all_stage_ids_in_vocabulary(self) -> None:
        actual = collect_stage_ids(self.caseplan)
        registered = vocab_stage_ids(self.vocab, "master")
        unregistered = actual - registered
        assert not unregistered, (
            f"Master caseplan.json has stage IDs not in vocabulary (master section): "
            f"{sorted(unregistered)}\nAdd them to case-vocabulary.yaml → stages.master"
        )

    def test_all_task_ids_in_vocabulary(self) -> None:
        actual = collect_task_ids(self.caseplan)
        registered = vocab_task_ids(self.vocab, "master")
        unregistered = actual - registered
        assert not unregistered, (
            f"Master caseplan.json has task IDs not in vocabulary (master section): "
            f"{sorted(unregistered)}\nAdd them to case-vocabulary.yaml → tasks.master"
        )

    def test_vocabulary_has_no_phantom_stage_ids(self) -> None:
        """Vocabulary must not claim stage IDs that don't exist in the caseplan."""
        actual = collect_stage_ids(self.caseplan)
        registered = vocab_stage_ids(self.vocab, "master")
        phantom = registered - actual
        assert not phantom, (
            f"case-vocabulary.yaml registers stage IDs not found in master caseplan.json: "
            f"{sorted(phantom)}\nRemove or correct them."
        )

    def test_vocabulary_has_no_phantom_task_ids(self) -> None:
        actual = collect_task_ids(self.caseplan)
        registered = vocab_task_ids(self.vocab, "master")
        phantom = registered - actual
        assert not phantom, (
            f"case-vocabulary.yaml registers task IDs not found in master caseplan.json: "
            f"{sorted(phantom)}\nRemove or correct them."
        )


class TestStakeholderParentCaseplan:
    """Validates clearflow-stakeholder-parent caseplan.json — skips if not yet authored."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.vocab = load_vocabulary()
        self.caseplan = load_caseplan(CANONICAL_CASEPLANS["stakeholder_parent"])

    def test_all_variable_names_in_vocabulary(self) -> None:
        if self.caseplan is None:
            pytest.skip("clearflow-stakeholder-parent not yet authored (Slice 010).")
        actual = collect_variable_names(self.caseplan)
        registered = vocab_variable_names(self.vocab, "stakeholder_parent")
        unregistered = actual - registered
        assert not unregistered, (
            f"Stakeholder-parent caseplan.json has variables not in vocabulary: {sorted(unregistered)}"
        )

    def test_all_stage_ids_in_vocabulary(self) -> None:
        if self.caseplan is None:
            pytest.skip("clearflow-stakeholder-parent not yet authored (Slice 010).")
        actual = collect_stage_ids(self.caseplan)
        registered = vocab_stage_ids(self.vocab, "stakeholder_parent")
        unregistered = actual - registered
        assert not unregistered, (
            f"Stakeholder-parent caseplan.json has stage IDs not in vocabulary: {sorted(unregistered)}"
        )

    def test_all_task_ids_in_vocabulary(self) -> None:
        if self.caseplan is None:
            pytest.skip("clearflow-stakeholder-parent not yet authored (Slice 010).")
        actual = collect_task_ids(self.caseplan)
        registered = vocab_task_ids(self.vocab, "stakeholder_parent")
        unregistered = actual - registered
        assert not unregistered, (
            f"Stakeholder-parent caseplan.json has task IDs not in vocabulary: {sorted(unregistered)}"
        )


class TestObligationGrandchildCaseplan:
    """Validates clearflow-obligation-grandchild caseplan.json — skips if not yet authored."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.vocab = load_vocabulary()
        self.caseplan = load_caseplan(CANONICAL_CASEPLANS["obligation_grandchild"])

    def test_all_variable_names_in_vocabulary(self) -> None:
        if self.caseplan is None:
            pytest.skip("clearflow-obligation-grandchild not yet authored (Slice 010).")
        actual = collect_variable_names(self.caseplan)
        registered = vocab_variable_names(self.vocab, "obligation_grandchild")
        unregistered = actual - registered
        assert not unregistered, (
            f"Obligation-grandchild caseplan.json has variables not in vocabulary: {sorted(unregistered)}"
        )

    def test_all_stage_ids_in_vocabulary(self) -> None:
        if self.caseplan is None:
            pytest.skip("clearflow-obligation-grandchild not yet authored (Slice 010).")
        actual = collect_stage_ids(self.caseplan)
        registered = vocab_stage_ids(self.vocab, "obligation_grandchild")
        unregistered = actual - registered
        assert not unregistered, (
            f"Obligation-grandchild caseplan.json has stage IDs not in vocabulary: {sorted(unregistered)}"
        )

    def test_all_task_ids_in_vocabulary(self) -> None:
        if self.caseplan is None:
            pytest.skip("clearflow-obligation-grandchild not yet authored (Slice 010).")
        actual = collect_task_ids(self.caseplan)
        registered = vocab_task_ids(self.vocab, "obligation_grandchild")
        unregistered = actual - registered
        assert not unregistered, (
            f"Obligation-grandchild caseplan.json has task IDs not in vocabulary: {sorted(unregistered)}"
        )


class TestVocabularyInternalConsistency:
    """Cross-section checks within the vocabulary file itself."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.vocab = load_vocabulary()

    def test_task_stage_ids_reference_registered_stages(self) -> None:
        """Every task.stage_id must match a registered stage in the same owner_case."""
        violations: list[str] = []
        for case_key in ("master", "stakeholder_parent", "obligation_grandchild"):
            stage_ids = vocab_stage_ids(self.vocab, case_key)
            tasks = self.vocab.get("tasks", {}).get(case_key, []) or []
            for t in tasks:
                sid = t.get("stage_id", "")
                if sid and sid not in stage_ids:
                    violations.append(
                        f"{case_key}.tasks[{t['id']}].stage_id={sid!r} not in {case_key} stages"
                    )
        assert not violations, "task.stage_id references unregistered stage:\n" + "\n".join(violations)

    def test_task_agent_keys_reference_registered_agents(self) -> None:
        """Every task with an agent_key must match a registered agent."""
        agent_keys = {a["key"] for a in self.vocab.get("agents", [])}
        violations: list[str] = []
        for case_key in ("master", "stakeholder_parent", "obligation_grandchild"):
            tasks = self.vocab.get("tasks", {}).get(case_key, []) or []
            for t in tasks:
                ak = t.get("agent_key", "")
                if ak and ak not in agent_keys:
                    violations.append(
                        f"{case_key}.tasks[{t['id']}].agent_key={ak!r} not in agents registry"
                    )
        assert not violations, "task.agent_key references unregistered agent:\n" + "\n".join(violations)

    def test_stakeholder_baa_ids_consistent(self) -> None:
        """Every provider stakeholder's baa_id must be in the BAA IDs derivable from providers."""
        providers = self.vocab.get("stakeholders", {}).get("providers", [])
        for p in providers:
            expected_baa_id = f"baa-{p['id']}"
            assert p.get("baa_id") == expected_baa_id, (
                f"Provider {p['id']} has baa_id={p.get('baa_id')!r}, expected {expected_baa_id!r}"
            )

    def test_event_types_list_is_not_empty(self) -> None:
        assert self.vocab.get("event_types"), "vocabulary.event_types must not be empty"

    def test_agent_keys_are_unique(self) -> None:
        keys = [a["key"] for a in self.vocab.get("agents", [])]
        assert len(keys) == len(set(keys)), f"Duplicate agent keys: {[k for k in keys if keys.count(k) > 1]}"
