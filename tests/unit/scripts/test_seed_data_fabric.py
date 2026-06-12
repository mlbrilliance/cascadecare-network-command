"""Slice 019 (c) — Data Fabric seed gate.

Runs `scripts/seed_data_fabric.sh --emit-json` (OFFLINE, no tenant) and validates
the seed document against `data-model.md`: entity coverage, row counts, FK
integrity, the 3 engineered BAA conflict patterns, the 2 Context Grounding
indexes, and IP-cleanliness of every seeded string. The live apply (T-c4) is a
human/online step.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "scripts" / "seed_data_fabric.sh"

FORBIDDEN = (
    "zelis", "aetna", "cigna", "unitedhealth", "cotiviti", "optum",
    "change healthcare", "wex ", "rivet", "bcbs", "hartley", "zipp", "zapp",
)

# Expected record counts per data-model.md.
EXPECTED_COUNTS = {
    "Provider": 6, "Payer": 4, "Vendor": 1, "Regulator": 1, "Insurer": 1,
    "Counsel": 1, "BAA": 6, "ClaimTelemetry": 30 * 24 * 6, "RegulatorTemplate": 1,
}


@pytest.fixture(scope="module")
def seed() -> dict:
    proc = subprocess.run(
        ["bash", str(SCRIPT), "--emit-json"],
        capture_output=True, text=True, timeout=120, cwd=str(REPO_ROOT),
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def test_script_and_generator_exist() -> None:
    assert SCRIPT.exists() and SCRIPT.stat().st_mode & 0o111
    assert (REPO_ROOT / "scripts" / "seed_data_fabric.py").exists()


def test_all_nine_entities_present(seed: dict) -> None:
    assert set(seed["entities"]) == set(EXPECTED_COUNTS)


@pytest.mark.parametrize("entity,count", EXPECTED_COUNTS.items())
def test_record_counts_match_data_model(seed: dict, entity: str, count: int) -> None:
    assert len(seed["entities"][entity]["records"]) == count


def test_every_entity_declares_a_schema(seed: dict) -> None:
    for entity, payload in seed["entities"].items():
        assert payload["schema"], f"{entity} has no schema"
        for field in payload["schema"]:
            assert field.get("name") and field.get("type")


def test_provider_baa_fk_resolves(seed: dict) -> None:
    baa_ids = {r["id"] for r in seed["entities"]["BAA"]["records"]}
    for prov in seed["entities"]["Provider"]["records"]:
        assert prov["baa_id"] in baa_ids, f"provider {prov['id']} → missing BAA"


def test_baa_provider_fk_resolves(seed: dict) -> None:
    provider_ids = {r["id"] for r in seed["entities"]["Provider"]["records"]}
    for baa in seed["entities"]["BAA"]["records"]:
        assert baa["provider_id"] in provider_ids


def test_claim_telemetry_fk_and_anomaly_onset(seed: dict) -> None:
    provider_ids = {r["id"] for r in seed["entities"]["Provider"]["records"]}
    rows = seed["entities"]["ClaimTelemetry"]["records"]
    assert all(r["provider_id"] in provider_ids for r in rows)
    # Every provider must carry the cascade anomaly (drives R1).
    flagged = {r["provider_id"] for r in rows if r["anomaly_flag"]}
    assert flagged == provider_ids, "all 6 providers must have anomaly rows"
    assert all(0.0 <= r["anomaly_score"] <= 1.0 for r in rows)


def test_three_baa_conflict_patterns_present(seed: dict) -> None:
    baas = {b["id"]: b for b in seed["entities"]["BAA"]["records"]}
    # Pattern 1: northstar 24h notify vs alpha pre-disclosure consultation.
    assert baas["baa-northstar"]["notification_window_hours"] == 24
    assert baas["baa-alpha"]["requires_pre_disclosure_consultation"] is True
    # Pattern 2: alpha forbids payer disclosure without consent (vs Apex demand).
    assert "payer_without_consent" in baas["baa-alpha"]["forbidden_disclosures"]
    # Pattern 3: beta permits federal reporting, epsilon forbids it.
    assert "federal_regulator" in baas["baa-beta"]["permitted_disclosures"]
    assert "federal_regulator" in baas["baa-epsilon"]["forbidden_disclosures"]


def test_two_context_grounding_indexes(seed: dict) -> None:
    assert seed["contextGroundingIndexes"] == ["BAA-corpus", "ClaimTelemetry-corpus"]


def test_seed_is_ip_clean(seed: dict) -> None:
    blob = json.dumps(seed).lower()
    hits = [tok for tok in FORBIDDEN if tok in blob]
    assert not hits, f"forbidden real-company tokens in seed: {hits}"


def test_seed_is_deterministic(seed: dict) -> None:
    """Re-running the generator yields byte-identical output (no randomness)."""
    again = subprocess.run(
        ["bash", str(SCRIPT), "--emit-json"],
        capture_output=True, text=True, timeout=120, cwd=str(REPO_ROOT),
    )
    assert again.returncode == 0
    assert json.loads(again.stdout) == seed


# --------------------------------------------------------------------------- #
# Live-translation helpers (pure functions; no tenant). Guard the contract     #
# verified live on 2026-06-04: DF rejects field name `id` and Text/Number/etc. #
# --------------------------------------------------------------------------- #

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "seed_data_fabric", REPO_ROOT / "scripts" / "seed_data_fabric.py"
)
seed_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(seed_mod)

_VALID_DF_TYPES = {"STRING", "INTEGER", "DECIMAL", "BOOLEAN", "DATETIME_WITH_TZ"}


def test_live_field_defs_use_valid_df_types_and_shape() -> None:
    for entity in seed_mod.SCHEMAS:
        for f in seed_mod.live_field_defs(entity):
            assert set(f) == {"fieldName", "type", "isRequired"}
            assert f["type"] in _VALID_DF_TYPES, (entity, f)


def test_live_field_names_have_no_underscore_and_no_id() -> None:
    # DF insert silently drops underscore-named fields; `id` is reserved.
    for entity in seed_mod.SCHEMAS:
        names = {f["fieldName"] for f in seed_mod.live_field_defs(entity)}
        assert "id" not in names, f"{entity} still emits reserved field 'id'"
        assert all("_" not in n for n in names), f"{entity} has underscore field: {names}"
        if "id" in seed_mod.SCHEMAS[entity]:
            assert "slug" in names, f"{entity} did not rename id->slug"


def test_live_field_name_mapping() -> None:
    assert seed_mod.live_field_name("id") == "slug"
    assert seed_mod.live_field_name("display_name") == "displayName"
    assert seed_mod.live_field_name("provider_id") == "providerId"
    assert seed_mod.live_field_name("business_continuity_runway_days") == "businessContinuityRunwayDays"
    assert seed_mod.live_field_name("vertical") == "vertical"


def test_live_record_renames_and_serializes_collections() -> None:
    rec = {"id": "alpha", "permitted_disclosures": ["regulator", "counsel"],
           "claim_count": 3, "anomaly_flag": True}
    out = seed_mod.live_record(rec)
    assert "id" not in out and out["slug"] == "alpha"
    assert out["permittedDisclosures"] == '["regulator", "counsel"]'  # JSON string, camel key
    assert out["claimCount"] == 3 and out["anomalyFlag"] is True  # scalars unchanged
