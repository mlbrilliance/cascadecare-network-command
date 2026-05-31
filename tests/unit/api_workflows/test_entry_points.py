"""Package-metadata gate for Slice 015 T016/T017 — API Workflow entry points.

Root cause of Orchestrator Error 2005 ("Entry points configuration
missing/corrupted") for the 14 `Type: "Api"` workflows: the solution packager
writes a `package-descriptor.json` whose `files` map declares
`content/entry-points.json` and `content/bindings_v2.json`, but for Api projects
the packager does NOT synthesize those two files — it only copies them from the
source dir. With no source copy, the descriptor points at absent files and
install fails.

Fix: each `api_workflows/<slug>/` commits an `entry-points.json` (V20 shape,
mirroring the case/coded-agent packages that install cleanly) and a
`bindings_v2.json` (empty — these workflows carry no Integration Service
connector activities yet). The packager then copies both into `content/`,
satisfying the descriptor.

This is a STRUCTURE gate on the committed files; the live install-confirm is
tenant-gated (carried forward). `scripts/gen_api_entry_points.py` regenerates
both files from each `main.json`; this test is its acceptance gate.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
API_ROOT = REPO_ROOT / "api_workflows"

ENTRY_POINT_SCHEMA = "https://cloud.uipath.com/draft/2024-12/entry-point"


def _workflow_slugs() -> list[str]:
    return sorted(
        d.name
        for d in API_ROOT.iterdir()
        if d.is_dir() and (d / "main.json").is_file()
    )


def _props(schema_doc: dict) -> dict:
    return schema_doc.get("schema", {}).get("document", {}).get("properties", {})


SLUGS = _workflow_slugs()


def test_fourteen_workflows_discovered() -> None:
    assert len(SLUGS) == 14, f"expected 14 API workflows, found {len(SLUGS)}: {SLUGS}"


@pytest.mark.parametrize("slug", SLUGS)
def test_entry_points_present_and_v20_shaped(slug: str) -> None:
    ep_path = API_ROOT / slug / "entry-points.json"
    assert ep_path.is_file(), f"{slug}: missing entry-points.json (Error 2005 cause)"
    ep = json.loads(ep_path.read_text())

    assert ep.get("$schema") == ENTRY_POINT_SCHEMA, f"{slug}: wrong $schema"
    assert ep.get("$id") == "entry-points.json", f"{slug}: wrong $id"
    entries = ep.get("entryPoints")
    assert isinstance(entries, list) and len(entries) == 1, f"{slug}: need exactly 1 entryPoint"

    e = entries[0]
    assert e.get("filePath") == "main.json", f"{slug}: filePath must point at the Api main file"
    assert e.get("type") == "process", f"{slug}: Api entry-point type must be 'process'"
    uid = e.get("uniqueId", "")
    assert isinstance(uid, str) and len(uid) == 36 and uid.count("-") == 4, (
        f"{slug}: uniqueId must be a GUID"
    )
    for io in ("input", "output"):
        assert e.get(io, {}).get("type") == "object", f"{slug}: {io} must be an object schema"
        assert "properties" in e[io], f"{slug}: {io} missing properties"


@pytest.mark.parametrize("slug", SLUGS)
def test_entry_point_io_matches_main(slug: str) -> None:
    """The entry-point input/output keys must mirror the workflow's own contract."""
    main = json.loads((API_ROOT / slug / "main.json").read_text())
    ep = json.loads((API_ROOT / slug / "entry-points.json").read_text())
    e = ep["entryPoints"][0]

    assert set(e["input"]["properties"]) == set(_props(main.get("input", {}))), (
        f"{slug}: entry-point input keys diverge from main.json input"
    )
    assert set(e["output"]["properties"]) == set(_props(main.get("output", {}))), (
        f"{slug}: entry-point output keys diverge from main.json output"
    )


@pytest.mark.parametrize("slug", SLUGS)
def test_bindings_present_and_canonical(slug: str) -> None:
    b_path = API_ROOT / slug / "bindings_v2.json"
    assert b_path.is_file(), f"{slug}: missing bindings_v2.json (descriptor declares it)"
    b = json.loads(b_path.read_text())
    assert b.get("version") == "2.0", f"{slug}: bindings must be version 2.0"
    assert b.get("resources") == [], f"{slug}: no IntSvc activities yet → empty resources"


@pytest.mark.parametrize("slug", SLUGS)
def test_unique_ids_are_distinct(slug: str) -> None:
    """Every entry point's GUID must be unique across the 14 packages."""
    ids = [
        json.loads((API_ROOT / s / "entry-points.json").read_text())["entryPoints"][0]["uniqueId"]
        for s in SLUGS
    ]
    assert len(ids) == len(set(ids)), "entry-point uniqueIds collide across workflows"
