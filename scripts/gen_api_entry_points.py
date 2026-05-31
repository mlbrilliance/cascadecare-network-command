#!/usr/bin/env python3
"""Generate per-package install metadata for the 14 Integration Service API Workflows.

WHY THIS EXISTS — Orchestrator Error 2005 ("Entry points configuration
missing/corrupted"). `uip solution pack` emits, for every `Type: "Api"` project,
a `package-descriptor.json` whose `files` map declares:

    operate.json      -> content/operate.json        (packager-generated)
    entry-points.json -> content/entry-points.json   (NOT generated for Api)
    bindings.json     -> content/bindings_v2.json     (NOT generated for Api)

The packager generates `operate.json` but *copies* the other two from the source
project dir. With no source copy they are absent from the nupkg, the descriptor
points at missing files, and Orchestrator install rejects the package (2005).

Coded-agent / Case / BPMN packages all ship a committed `entry-points.json`; the
API workflows were the only package type missing one. This script closes that gap
by deriving both files from each workflow's `main.json` contract.

Reproducible, idempotent build-time tooling (mirrors scripts/pack-solution.sh).
Re-run after editing any `api_workflows/<slug>/main.json`.

ENTRY-POINT SHAPE — V20 (`https://cloud.uipath.com/draft/2024-12/entry-point`),
the same shape the installing Case/coded-agent packages use:
  - filePath: "main.json"   (the Api project's main workflow file)
  - type: "process"         (the workflow installs as a process resource —
                             the packager writes it to resources/.../process/api/;
                             this exact token is the one tenant-gated unknown and
                             is verified on first live install — see slice tasks)
  - uniqueId: deterministic uuid5(slug) so reruns are stable and the 14 GUIDs
              never collide
  - input/output: lifted verbatim from main.json's input/output JSON schemas

bindings_v2.json is the canonical empty shape — these workflows carry no
Integration Service connector activities yet (a live Data Fabric connector read
is wired at deploy via `uip api-workflow registry stub`).
"""

from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = REPO_ROOT / "api_workflows"

ENTRY_POINT_SCHEMA = "https://cloud.uipath.com/draft/2024-12/entry-point"
# Fixed namespace so uuid5(NAMESPACE, slug) is stable across machines and reruns.
NAMESPACE = uuid.UUID("c45cadec-a4e0-4f10-9b00-0000c45cadec")


def _schema_document(io_block: dict) -> dict:
    """Return the JSON-schema `document` for an input/output block, sans wrapper."""
    return io_block.get("schema", {}).get("document", {})


def _entry_points(slug: str, main: dict) -> dict:
    in_doc = _schema_document(main.get("input", {}))
    out_doc = _schema_document(main.get("output", {}))
    return {
        "$schema": ENTRY_POINT_SCHEMA,
        "$id": "entry-points.json",
        "entryPoints": [
            {
                "filePath": "main.json",
                "uniqueId": str(uuid.uuid5(NAMESPACE, slug)),
                "type": "process",
                "input": {
                    "type": "object",
                    "properties": in_doc.get("properties", {}),
                },
                "output": {
                    "type": "object",
                    "properties": out_doc.get("properties", {}),
                },
            }
        ],
    }


def _bindings() -> dict:
    return {"version": "2.0", "resources": []}


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n")


def main() -> int:
    if not API_ROOT.is_dir():
        print(f"error: {API_ROOT} not found", file=sys.stderr)
        return 1

    slugs = sorted(d.name for d in API_ROOT.iterdir() if d.is_dir() and (d / "main.json").is_file())
    if not slugs:
        print("error: no api_workflows/<slug>/main.json found", file=sys.stderr)
        return 1

    for slug in slugs:
        wf_dir = API_ROOT / slug
        main_doc = json.loads((wf_dir / "main.json").read_text())
        _write_json(wf_dir / "entry-points.json", _entry_points(slug, main_doc))
        _write_json(wf_dir / "bindings_v2.json", _bindings())
        print(f"  {slug}: entry-points.json + bindings_v2.json")

    print(f"==> generated install metadata for {len(slugs)} API workflows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
