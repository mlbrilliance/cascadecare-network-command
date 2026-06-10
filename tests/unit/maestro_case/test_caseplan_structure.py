"""V20 structural-conformance tests for every Maestro Case caseplan.json.

The caseplan is the core runtime artifact (the canvas IS the orchestrator),
so it gets the same structural guard the event contracts get. These assertions
encode the V20 recipe from the uipath-maestro-case skill: object-shaped
variables, the required metadata markers, per-task elementId, and referential
integrity of edges. Discovers every maestro_case/**/caseplan.json so a
new caseplan (parent/grandchild, Slice 010) is covered automatically.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
MAESTRO_ROOT = REPO_ROOT / "maestro_case"

CASEPLANS = sorted(MAESTRO_ROOT.glob("**/caseplan.json"))

# Required V20 metadata markers (uipath-maestro-case skill, case-schema.md).
# Studio Web canvas regens (v1.0.14+) stopped emitting `displayName` — the
# canvas-emitted shape is live-proven ground truth, so it is no longer required.
REQUIRED_METADATA = {
    "caseUnifiedSchemaEnabled",
    "publishVersion",
    "intsvcActivityConfig",
    "caseAppEnabled",
    "caseIdentifierType",
    "caseIdentifier",
}
REQUIRED_TOP_LEVEL = {"id", "version", "name", "metadata", "variables", "nodes", "edges"}
VARIABLE_BUCKETS = ("inputs", "outputs", "inputOutputs")


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _iter_tasks(node: dict[str, Any]) -> list[dict[str, Any]]:
    """Yield task dicts from a stage node.

    V20 groups tasks as a list-of-lists (data.tasks = [[task, ...], ...]);
    tolerate a flat list of task dicts too.
    """
    data = node.get("data", {})
    if not isinstance(data, dict):
        return []
    tasks: list[dict[str, Any]] = []
    for entry in data.get("tasks", []):
        if isinstance(entry, list):
            tasks.extend(t for t in entry if isinstance(t, dict))
        elif isinstance(entry, dict):
            tasks.append(entry)
    return tasks


# Parametrize over discovered caseplans; label by repo-relative path for readable failures.
PARAMS = [pytest.param(p, id=str(p.relative_to(MAESTRO_ROOT))) for p in CASEPLANS]


def test_at_least_one_caseplan_exists() -> None:
    assert CASEPLANS, "No maestro_case/**/caseplan.json found (master required from Slice 003)."


@pytest.mark.parametrize("path", PARAMS)
class TestCaseplanV20:
    def test_version_is_v20(self, path: Path) -> None:
        # Canvas round-trips bump the schema version (20.0.0 -> 23.0.0 as of
        # 2026-06); anything >= 20 is the V20-family schema this suite encodes.
        caseplan = _load(path)
        major = str(caseplan.get("version", "")).split(".")[0]
        assert major.isdigit() and int(major) >= 20, (
            f"{path} version must be V20-family (got {caseplan.get('version')!r})"
        )

    def test_required_top_level_keys(self, path: Path) -> None:
        caseplan = _load(path)
        missing = REQUIRED_TOP_LEVEL - set(caseplan)
        assert not missing, f"{path} missing top-level keys: {sorted(missing)}"

    def test_variables_are_object_shaped(self, path: Path) -> None:
        variables = _load(path).get("variables")
        assert isinstance(variables, dict), (
            f"{path} variables must be the V20 object shape, not an array"
        )
        for bucket in VARIABLE_BUCKETS:
            assert bucket in variables, f"{path} variables missing '{bucket}' bucket"
            assert isinstance(variables[bucket], list), f"{path} variables.{bucket} must be a list"

    def test_metadata_has_v20_markers(self, path: Path) -> None:
        metadata = _load(path).get("metadata", {})
        missing = REQUIRED_METADATA - set(metadata)
        assert not missing, f"{path} metadata missing V20 markers: {sorted(missing)}"

    def test_every_task_has_qualified_element_id(self, path: Path) -> None:
        caseplan = _load(path)
        offenders: list[str] = []
        task_count = 0
        for node in caseplan.get("nodes", []):
            stage_id = node.get("id", "")
            for task in _iter_tasks(node):
                task_count += 1
                expected = f"{stage_id}-{task.get('id', '')}"
                if task.get("elementId") != expected:
                    offenders.append(f"{task.get('id')} -> {task.get('elementId')!r} (want {expected!r})")
        assert not offenders, f"{path} tasks with wrong/missing elementId: {offenders}"
        assert task_count > 0, f"{path} has no tasks to check"

    def test_edges_reference_existing_nodes(self, path: Path) -> None:
        caseplan = _load(path)
        node_ids = {n.get("id") for n in caseplan.get("nodes", [])}
        dangling: list[str] = []
        for edge in caseplan.get("edges", []):
            for end in ("source", "target"):
                ref = edge.get(end)
                if ref is not None and ref not in node_ids:
                    dangling.append(f"edge {edge.get('id')} {end}={ref!r}")
        assert not dangling, f"{path} edges reference missing nodes: {dangling}"
