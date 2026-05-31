"""Structural gate for the Slice 012 Maestro Flow Demo Driver.

The driver fires the API Workflows that drive the five reversals. Offline this
checks the flow is valid JSON, carries every reversal's event_type, and names
the key external-system slugs that produce the hero beats. (Live node binding +
`uip maestro flow validate` happen at deploy.)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
FLOW_PATH = REPO_ROOT / "maestro_flow" / "clearflow-demo-driver" / "clearflow-demo-driver.flow"
VOCAB_PATH = REPO_ROOT / "specs" / "003-uipath-native" / "case-vocabulary.yaml"

EXPECTED_EVENT_TYPES = [
    "provider-claim-anomaly",
    "multi-customer-correlation",
    "vendor-attribution",
    "regulatory-subpoena",
    "payer-demand",
    "insurer-directive",
    "litigation-event",
]
# Slugs that produce the reversal beats; must be registered source_systems.
KEY_SLUGS = ["provider-northstar", "vendor-nimbus", "regulator-tn-doi", "payer-apex", "insurer-aurora-specialty"]


def test_flow_is_valid_json_with_nodes_and_edges() -> None:
    flow = json.loads(FLOW_PATH.read_text(encoding="utf-8"))
    assert isinstance(flow.get("nodes"), list), "flow must have a nodes list"
    assert flow["nodes"], "flow nodes list must be non-empty"
    assert isinstance(flow.get("edges"), list), "flow must have an edges list"


@pytest.mark.parametrize("event_type", EXPECTED_EVENT_TYPES)
def test_every_reversal_event_is_driven(event_type: str) -> None:
    text = FLOW_PATH.read_text(encoding="utf-8")
    assert event_type in text, f"Demo Driver does not drive event_type {event_type!r}"


def test_key_slugs_are_registered_source_systems() -> None:
    text = FLOW_PATH.read_text(encoding="utf-8")
    registered = set(yaml.safe_load(VOCAB_PATH.read_text()).get("source_systems", []))
    for slug in KEY_SLUGS:
        assert slug in text, f"Demo Driver does not reference {slug!r}"
        assert slug in registered, f"{slug!r} not a registered source_system"
