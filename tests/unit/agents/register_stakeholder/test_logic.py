"""Mock coded process — Register Stakeholder & Pull BAA: deterministic-core tests."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from types import ModuleType

REPO_ROOT = Path(__file__).parents[4]
AGENT_PY = REPO_ROOT / "agents" / "register-stakeholder" / "agent.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("register_stakeholder_uut", AGENT_PY)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def agent() -> ModuleType:
    assert AGENT_PY.exists(), f"agent.py not found at {AGENT_PY}"
    return _load()


def test_registers_known_provider(agent: ModuleType) -> None:
    out = agent.main(agent.Input(provider_slug="northstar", master_case_id="m1"))
    assert out.onboarding_status == "registered"
    assert out.baa_id == "BAA-NORTHSTAR"
    assert "Northstar Regional Health" in out.summary
    assert out.error_type == ""


def test_empty_inputs_still_complete(agent: ModuleType) -> None:
    out = agent.main(agent.Input())
    assert out.onboarding_status == "registered"
    assert out.baa_id == "BAA-UNASSIGNED"
    assert out.error_type == ""


def test_stakeholder_id_fallback(agent: ModuleType) -> None:
    out = agent.main(agent.Input(stakeholder_id="alpha"))
    assert out.baa_id == "BAA-ALPHA"
    assert out.stakeholder_id == "alpha"


def test_deterministic(agent: ModuleType) -> None:
    a = agent.main(agent.Input(provider_slug="beta"))
    b = agent.main(agent.Input(provider_slug="beta"))
    assert a.model_dump() == b.model_dump()
