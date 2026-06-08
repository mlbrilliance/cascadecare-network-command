"""Mock coded process — Generate Audit Record: deterministic-core tests."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from types import ModuleType

REPO_ROOT = Path(__file__).parents[4]
AGENT_PY = REPO_ROOT / "agents" / "generate-audit-record" / "agent.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("generate_audit_record_uut", AGENT_PY)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def agent() -> ModuleType:
    assert AGENT_PY.exists(), f"agent.py not found at {AGENT_PY}"
    return _load()


def test_generates_audit_id(agent: ModuleType) -> None:
    out = agent.main(agent.Input(obligation_id="obl-7", disposition="filed", recorded_at="2026-06-07T00:00:00Z"))
    assert out.audit_record_id == "AUD-OBL-7"
    assert out.disposition == "filed"
    assert out.recorded_at == "2026-06-07T00:00:00Z"  # echoed, never generated
    assert out.error_type == ""


def test_timestamp_is_echoed_not_generated(agent: ModuleType) -> None:
    out = agent.main(agent.Input(obligation_id="x"))
    assert out.recorded_at == ""  # no Date.now(); empty when not supplied


def test_empty_inputs_complete(agent: ModuleType) -> None:
    out = agent.main(agent.Input())
    assert out.audit_record_id == "AUD-UNASSIGNED"
    assert out.disposition == "recorded"
    assert out.error_type == ""
