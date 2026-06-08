"""Mock coded process — Classify Obligation: deterministic-core tests."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from types import ModuleType

REPO_ROOT = Path(__file__).parents[4]
AGENT_PY = REPO_ROOT / "agents" / "classify-obligation" / "agent.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("classify_obligation_uut", AGENT_PY)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def agent() -> ModuleType:
    assert AGENT_PY.exists(), f"agent.py not found at {AGENT_PY}"
    return _load()


def test_subpoena_is_high(agent: ModuleType) -> None:
    out = agent.main(agent.Input(obligation_type="subpoena-response", jurisdiction="TN-DOI", baa_id="BAA-NORTHSTAR"))
    assert out.severity == "high"
    assert "TN-DOI" in out.summary
    assert out.error_type == ""


def test_audit_is_medium(agent: ModuleType) -> None:
    out = agent.main(agent.Input(obligation_type="audit-cooperation"))
    assert out.severity == "medium"


def test_default_is_low(agent: ModuleType) -> None:
    out = agent.main(agent.Input(obligation_type="routine-notice"))
    assert out.severity == "low"


def test_empty_inputs_complete(agent: ModuleType) -> None:
    out = agent.main(agent.Input())
    assert out.error_type == ""
    assert out.obligation_type == "general-obligation"
