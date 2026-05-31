"""Registry-consistency gate for Slices 008 (low-code) + 009 (coded) agents.

Every agent registered in case-vocabulary.yaml must have its project directory
(named by the vocabulary `key`) and its authoritative prompt file. Low-code
agents (`agent-builder`) carry an agent.json whose system prompt equals the .md;
coded agents carry a uipath.json + a build-system-free pyproject.toml.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
VOCAB_PATH = REPO_ROOT / "specs" / "003-uipath-native" / "case-vocabulary.yaml"
AGENTS_ROOT = REPO_ROOT / "agents"
PROMPTS_ROOT = AGENTS_ROOT / "prompts"

AGENTS = yaml.safe_load(VOCAB_PATH.read_text()).get("agents", [])
PARAMS = [pytest.param(a, id=a["key"]) for a in AGENTS]
EXPECTED_AGENT_COUNT = 7  # 4 Agent Builder (low-code) + 3 Coded (Python SDK)


def test_seven_agents_registered() -> None:
    assert len(AGENTS) == EXPECTED_AGENT_COUNT, (
        f"expected {EXPECTED_AGENT_COUNT} agents in vocabulary, got {len(AGENTS)}"
    )


@pytest.mark.parametrize("agent", PARAMS)
class TestAgentArtifacts:
    def test_agent_dir_exists(self, agent: dict) -> None:
        assert (AGENTS_ROOT / agent["key"]).is_dir(), (
            f"missing agent dir agents/{agent['key']}/"
        )

    def test_prompt_file_exists_and_nonempty(self, agent: dict) -> None:
        p = PROMPTS_ROOT / agent["prompt_file"]
        assert p.is_file(), f"missing prompt agents/prompts/{agent['prompt_file']}"
        assert p.read_text(encoding="utf-8").strip(), f"empty prompt {p}"

    def test_lowcode_agent_json_matches_prompt(self, agent: dict) -> None:
        if agent["agent_type"] != "agent-builder":
            pytest.skip("not a low-code agent")
        aj = AGENTS_ROOT / agent["key"] / "agent.json"
        assert aj.is_file(), f"missing {aj}"
        doc = json.loads(aj.read_text(encoding="utf-8"))
        assert doc.get("type") == "lowCode", f"{aj}: type must be lowCode"
        assert doc.get("settings", {}).get("model"), f"{aj}: settings.model required"
        system = next((m for m in doc.get("messages", []) if m.get("role") == "system"), None)
        assert system is not None, f"{aj}: no system message"
        prompt_text = (PROMPTS_ROOT / agent["prompt_file"]).read_text(encoding="utf-8").strip()
        assert system["content"].strip() == prompt_text, (
            f"{aj}: system message content drifted from agents/prompts/{agent['prompt_file']}"
        )

    def test_coded_agent_package_shape(self, agent: dict) -> None:
        if agent["agent_type"] != "coded":
            pytest.skip("not a coded agent")
        d = AGENTS_ROOT / agent["key"]
        assert (d / "uipath.json").is_file(), f"missing {d}/uipath.json"
        pyproj = d / "pyproject.toml"
        assert pyproj.is_file(), f"missing {d}/pyproject.toml"
        assert "[build-system]" not in pyproj.read_text(encoding="utf-8"), (
            f"{pyproj}: coded agents must NOT declare a [build-system]"
        )
