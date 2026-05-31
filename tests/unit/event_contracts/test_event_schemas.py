"""
Candidate 4 — Event Contract Schema Tests

Verifies that:
1. Every event schema file under specs/003-uipath-native/event-contracts/ is
   valid JSON Schema draft-07.
2. Every schema has the mandatory envelope: event_type (const), source_system,
   simulated_day, and a maestro_trigger_filter_hint annotation.
3. Golden fixture files in tests/unit/event_contracts/fixtures/ validate
   against their corresponding schema.
4. The set of event_type const values in the schemas matches
   vocabulary.event_types in case-vocabulary.yaml exactly (no orphans, no
   missing entries).

Design decisions:
- Schema files are discovered by glob; adding a new schema file automatically
  adds it to every check.
- The vocabulary cross-check ensures Candidate 3 and Candidate 4 stay in sync.
- jsonschema.Draft7Validator is used so we get the same semantics Maestro
  Trigger authoring tools expect.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema
import pytest
import yaml

REPO_ROOT = Path(__file__).parents[3]
CONTRACTS_DIR = REPO_ROOT / "specs" / "003-uipath-native" / "event-contracts"
FIXTURES_DIR = Path(__file__).parent / "fixtures"
VOCAB_PATH = REPO_ROOT / "specs" / "003-uipath-native" / "case-vocabulary.yaml"

# Required envelope fields in every event schema's "required" array.
ENVELOPE_REQUIRED = {"event_type", "source_system", "simulated_day"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_all_schemas() -> dict[str, dict[str, Any]]:
    """Return {stem: schema_dict} for every *.json-schema.json file found."""
    if not CONTRACTS_DIR.exists():
        return {}
    return {
        p.stem.removesuffix(".json-schema"): json.loads(p.read_text())
        for p in sorted(CONTRACTS_DIR.glob("*.json-schema.json"))
    }


def load_vocabulary_event_types() -> set[str]:
    if not VOCAB_PATH.exists():
        return set()
    vocab = yaml.safe_load(VOCAB_PATH.read_text())
    return set(vocab.get("event_types", []))


def load_vocabulary_source_systems() -> set[str]:
    if not VOCAB_PATH.exists():
        return set()
    vocab = yaml.safe_load(VOCAB_PATH.read_text())
    return set(vocab.get("source_systems", []))


def get_source_system_values(schema: dict[str, Any]) -> list[str]:
    """Return the allowed source_system values (enum or const) for a schema."""
    ss = schema.get("properties", {}).get("source_system", {})
    if "enum" in ss:
        return list(ss["enum"])
    if "const" in ss:
        return [ss["const"]]
    return []


def get_event_type_const(schema: dict[str, Any]) -> str | None:
    return schema.get("properties", {}).get("event_type", {}).get("const")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestSchemaFilesExist:
    def test_contracts_directory_exists(self) -> None:
        assert CONTRACTS_DIR.exists(), (
            f"event-contracts/ directory not found at {CONTRACTS_DIR}. "
            "Create it with one *.json-schema.json per event type."
        )

    def test_at_least_one_schema_file(self) -> None:
        schemas = load_all_schemas()
        assert schemas, (
            f"No *.json-schema.json files found in {CONTRACTS_DIR}. "
            "Create one per event type listed in case-vocabulary.yaml → event_types."
        )

    def test_expected_event_types_all_have_schemas(self) -> None:
        """Every event type in the vocabulary must have a corresponding schema file."""
        vocab_types = load_vocabulary_event_types()
        schema_types = set(load_all_schemas().keys())
        missing = vocab_types - schema_types
        assert not missing, (
            f"No schema file for event types: {sorted(missing)}\n"
            f"Create specs/003-uipath-native/event-contracts/<event-type>.json-schema.json"
        )

    def test_no_orphan_schemas(self) -> None:
        """Every schema file must correspond to a vocabulary event_type."""
        vocab_types = load_vocabulary_event_types()
        schema_types = set(load_all_schemas().keys())
        orphans = schema_types - vocab_types
        assert not orphans, (
            f"Schema files have no matching event_type in vocabulary: {sorted(orphans)}\n"
            "Either add them to case-vocabulary.yaml → event_types or remove the schema files."
        )


class TestSchemaEnvelope:
    """Per-schema structural checks — parameterised over all discovered schemas."""

    @pytest.fixture(params=list(load_all_schemas().keys()) if CONTRACTS_DIR.exists() else [])
    def schema_entry(self, request: pytest.FixtureRequest) -> tuple[str, dict[str, Any]]:
        name: str = request.param
        schemas = load_all_schemas()
        return name, schemas[name]

    def test_is_valid_json(self, schema_entry: tuple[str, dict[str, Any]]) -> None:
        # If we got here, json.loads already succeeded in load_all_schemas.
        name, schema = schema_entry
        assert isinstance(schema, dict), f"{name}: top level must be a JSON object"

    def test_has_draft7_schema_keyword(self, schema_entry: tuple[str, dict[str, Any]]) -> None:
        name, schema = schema_entry
        assert schema.get("$schema") == "http://json-schema.org/draft-07/schema#", (
            f"{name}: missing or incorrect $schema — must be "
            "'http://json-schema.org/draft-07/schema#'"
        )

    def test_is_valid_draft7_meta_schema(self, schema_entry: tuple[str, dict[str, Any]]) -> None:
        name, schema = schema_entry
        try:
            jsonschema.Draft7Validator.check_schema(schema)
        except jsonschema.SchemaError as exc:
            pytest.fail(f"{name} is not a valid JSON Schema draft-07: {exc.message}")

    def test_has_required_envelope_fields(self, schema_entry: tuple[str, dict[str, Any]]) -> None:
        name, schema = schema_entry
        required = set(schema.get("required", []))
        missing = ENVELOPE_REQUIRED - required
        assert not missing, (
            f"{name}: 'required' array must include {sorted(ENVELOPE_REQUIRED)}. "
            f"Missing: {sorted(missing)}"
        )

    def test_event_type_is_const(self, schema_entry: tuple[str, dict[str, Any]]) -> None:
        name, schema = schema_entry
        et = schema.get("properties", {}).get("event_type", {})
        assert "const" in et, (
            f"{name}: properties.event_type must have a 'const' value (exact string, not free-form)"
        )

    def test_event_type_const_matches_filename(self, schema_entry: tuple[str, dict[str, Any]]) -> None:
        name, schema = schema_entry
        const_val = get_event_type_const(schema)
        assert const_val == name, (
            f"{name}: event_type.const={const_val!r} must match the filename stem {name!r}"
        )

    def test_event_type_const_in_vocabulary(self, schema_entry: tuple[str, dict[str, Any]]) -> None:
        name, schema = schema_entry
        vocab_types = load_vocabulary_event_types()
        if not vocab_types:
            pytest.skip("Vocabulary not found — cannot cross-check event_type against it.")
        const_val = get_event_type_const(schema)
        assert const_val in vocab_types, (
            f"{name}: event_type.const={const_val!r} not in vocabulary.event_types. "
            "Add it to case-vocabulary.yaml or correct the schema."
        )

    def test_has_maestro_trigger_filter_hint(self, schema_entry: tuple[str, dict[str, Any]]) -> None:
        name, schema = schema_entry
        hint = schema.get("maestro_trigger_filter_hint")
        assert hint is not None, (
            f"{name}: missing 'maestro_trigger_filter_hint' annotation. "
            "Add it as a top-level non-validating key with a 'filterTree' suggestion."
        )
        assert "filterTree" in hint, (
            f"{name}: maestro_trigger_filter_hint must contain a 'filterTree' key."
        )

    def test_simulated_day_has_integer_type(self, schema_entry: tuple[str, dict[str, Any]]) -> None:
        name, schema = schema_entry
        day_prop = schema.get("properties", {}).get("simulated_day", {})
        assert day_prop.get("type") == "integer", (
            f"{name}: properties.simulated_day must have type=integer"
        )

    def test_source_system_has_enum(self, schema_entry: tuple[str, dict[str, Any]]) -> None:
        name, schema = schema_entry
        ss_prop = schema.get("properties", {}).get("source_system", {})
        assert "enum" in ss_prop or "const" in ss_prop, (
            f"{name}: properties.source_system should restrict allowed values with 'enum' or 'const'"
        )

    def test_source_system_values_in_vocabulary(self, schema_entry: tuple[str, dict[str, Any]]) -> None:
        """Every source_system value a schema allows must be a registered vocabulary source_system."""
        name, schema = schema_entry
        vocab_sources = load_vocabulary_source_systems()
        if not vocab_sources:
            pytest.skip(
                "vocabulary.source_systems not found — add a source_systems list to "
                "case-vocabulary.yaml to enable this cross-check."
            )
        schema_values = set(get_source_system_values(schema))
        missing = schema_values - vocab_sources
        assert not missing, (
            f"{name}: source_system value(s) {sorted(missing)} not in vocabulary.source_systems. "
            "Add them to case-vocabulary.yaml → source_systems or correct the schema."
        )


class TestGoldenFixtures:
    """Validates golden fixture files against their corresponding schemas."""

    @pytest.fixture(params=sorted(FIXTURES_DIR.glob("*.json")) if FIXTURES_DIR.exists() else [])
    def fixture_entry(self, request: pytest.FixtureRequest) -> tuple[str, dict[str, Any]]:
        path: Path = request.param
        return path.stem, json.loads(path.read_text())

    def test_fixtures_directory_exists(self) -> None:
        assert FIXTURES_DIR.exists(), (
            f"fixtures/ directory not found at {FIXTURES_DIR}. "
            "Create one golden fixture JSON per event type."
        )

    def test_has_fixture_for_every_schema(self) -> None:
        schemas = load_all_schemas()
        fixture_stems = {p.stem for p in FIXTURES_DIR.glob("*.json")} if FIXTURES_DIR.exists() else set()
        missing = set(schemas.keys()) - fixture_stems
        assert not missing, (
            f"No golden fixture for schemas: {sorted(missing)}. "
            "Create tests/unit/event_contracts/fixtures/<event-type>.json"
        )

    def test_fixture_validates_against_schema(self, fixture_entry: tuple[str, dict[str, Any]]) -> None:
        name, fixture = fixture_entry
        schemas = load_all_schemas()
        if name not in schemas:
            pytest.skip(f"No schema found for fixture {name!r} — schema not yet authored.")
        schema = schemas[name]
        try:
            validator = jsonschema.Draft7Validator(schema)
            errors = list(validator.iter_errors(fixture))
        except jsonschema.SchemaError as exc:
            pytest.fail(f"Schema {name!r} is invalid: {exc.message}")
        if errors:
            messages = "\n".join(f"  - {e.json_path}: {e.message}" for e in errors)
            pytest.fail(f"Fixture {name!r} failed schema validation:\n{messages}")

    def test_fixture_event_type_matches_filename(self, fixture_entry: tuple[str, dict[str, Any]]) -> None:
        name, fixture = fixture_entry
        assert fixture.get("event_type") == name, (
            f"Fixture {name}.json has event_type={fixture.get('event_type')!r}, "
            f"expected {name!r} to match filename."
        )
