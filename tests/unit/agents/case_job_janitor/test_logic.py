"""Slice 023 — Case-Job Janitor: deterministic-core tests (TDD).

Imported BY PATH so it runs under repo-root `uv run pytest` with no UiPath auth.
Covers the zombie-selection rule (prefix + min-age, unparseable start skipped),
the sweep orchestration (dry-run stops nothing, single-key doubled for the bulk
endpoint, stop failure surfaces SWEEP_FAILED), and the never-raise entrypoint
contract.

Background (proven live 2026-06-12): completed Maestro case instances never flip
their Orchestrator job to Successful — the job row says Running forever. Only the
bulk StopJobs endpoint (2+ keys) force-stops instantly; killing the job shell does
not touch the case instance.
"""

from __future__ import annotations

import importlib.util
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from types import ModuleType

REPO_ROOT = Path(__file__).parents[4]
AGENT_PY = REPO_ROOT / "agents" / "case-job-janitor" / "agent.py"

NOW = datetime(2026, 6, 12, 12, 0, 0, tzinfo=timezone.utc)


def _load_agent() -> ModuleType:
    spec = importlib.util.spec_from_file_location("janitor_agent_under_test", AGENT_PY)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def agent() -> ModuleType:
    assert AGENT_PY.exists(), f"agent.py not found at {AGENT_PY}"
    return _load_agent()


def _job(key: str, name: str, age_hours: float | None) -> dict[str, Any]:
    start = None if age_hours is None else (NOW - timedelta(hours=age_hours)).isoformat()
    return {"key": key, "process_name": name, "start_time": start}


class TestImportsWithoutAuth:
    def test_module_imports_without_uipath_auth(self, agent: ModuleType) -> None:
        assert hasattr(agent, "select_zombies")
        assert hasattr(agent, "run_sweep")
        assert hasattr(agent, "Input")
        assert hasattr(agent, "Output")
        assert hasattr(agent, "main")


class TestSelectZombies:
    def test_old_clearflow_job_is_eligible(self, agent: ModuleType) -> None:
        jobs = [_job("k1", "clearflow-stakeholder-parent", age_hours=25)]
        eligible, scanned, skipped = agent.select_zombies(jobs, "clearflow", 24.0, NOW)
        assert eligible == ["k1"]
        assert scanned == 1
        assert skipped == 0

    def test_young_job_is_protected(self, agent: ModuleType) -> None:
        jobs = [_job("k1", "clearflow-master-crisis", age_hours=1)]
        eligible, scanned, skipped = agent.select_zombies(jobs, "clearflow", 24.0, NOW)
        assert eligible == []
        assert scanned == 1
        assert skipped == 1

    def test_exact_threshold_is_eligible(self, agent: ModuleType) -> None:
        jobs = [_job("k1", "clearflow-obligation-grandchild", age_hours=24)]
        eligible, _, _ = agent.select_zombies(jobs, "clearflow", 24.0, NOW)
        assert eligible == ["k1"]

    def test_non_prefix_jobs_are_invisible(self, agent: ModuleType) -> None:
        jobs = [_job("k1", "some-other-process", age_hours=100)]
        eligible, scanned, skipped = agent.select_zombies(jobs, "clearflow", 24.0, NOW)
        assert eligible == []
        assert scanned == 0
        assert skipped == 0

    def test_unparseable_start_time_is_never_stopped(self, agent: ModuleType) -> None:
        jobs = [
            {"key": "k1", "process_name": "clearflow-master-crisis", "start_time": "not-a-date"},
            _job("k2", "clearflow-master-crisis", age_hours=None),
        ]
        eligible, scanned, skipped = agent.select_zombies(jobs, "clearflow", 24.0, NOW)
        assert eligible == []
        assert scanned == 2
        assert skipped == 2

    def test_mixed_population(self, agent: ModuleType) -> None:
        jobs = [
            _job("old1", "clearflow-stakeholder-parent", age_hours=30),
            _job("old2", "clearflow-obligation-grandchild", age_hours=72),
            _job("young", "clearflow-master-crisis", age_hours=0.5),
            _job("other", "vendor-sync", age_hours=999),
        ]
        eligible, scanned, skipped = agent.select_zombies(jobs, "clearflow", 24.0, NOW)
        assert eligible == ["old1", "old2"]
        assert scanned == 3
        assert skipped == 1


class TestCreationTimeFallback:
    """v0.2.0: age falls back to creation_time when start_time is missing —
    Maestro Agentic/Pending jobs can carry an empty StartTime."""

    def _iso(self, age_hours: float) -> str:
        return (NOW - timedelta(hours=age_hours)).isoformat()

    def test_null_start_old_creation_is_eligible(self, agent: ModuleType) -> None:
        jobs = [{"key": "k1", "process_name": "clearflow-obligation-grandchild",
                 "start_time": None, "creation_time": self._iso(30)}]
        eligible, scanned, skipped = agent.select_zombies(jobs, "clearflow", 24.0, NOW)
        assert eligible == ["k1"]
        assert scanned == 1
        assert skipped == 0

    def test_null_start_young_creation_is_protected(self, agent: ModuleType) -> None:
        jobs = [{"key": "k1", "process_name": "clearflow-master-crisis",
                 "start_time": "", "creation_time": self._iso(1)}]
        eligible, _, skipped = agent.select_zombies(jobs, "clearflow", 24.0, NOW)
        assert eligible == []
        assert skipped == 1

    def test_both_timestamps_missing_is_skipped(self, agent: ModuleType) -> None:
        jobs = [{"key": "k1", "process_name": "clearflow-master-crisis",
                 "start_time": None, "creation_time": None}]
        eligible, _, skipped = agent.select_zombies(jobs, "clearflow", 24.0, NOW)
        assert eligible == []
        assert skipped == 1

    def test_start_time_takes_precedence(self, agent: ModuleType) -> None:
        # start_time young (protect) even though creation_time is old.
        jobs = [{"key": "k1", "process_name": "clearflow-master-crisis",
                 "start_time": self._iso(1), "creation_time": self._iso(99)}]
        eligible, _, skipped = agent.select_zombies(jobs, "clearflow", 24.0, NOW)
        assert eligible == []
        assert skipped == 1


class _StopRecorder:
    def __init__(self, fail: bool = False) -> None:
        self.calls: list[list[str]] = []
        self.fail = fail

    def __call__(self, keys: list[str]) -> None:
        self.calls.append(list(keys))
        if self.fail:
            raise RuntimeError("boom: StopJobs 500")


class TestRunSweep:
    def _input(self, agent: ModuleType, **overrides: Any) -> Any:
        return agent.Input(**overrides)

    def test_happy_path_bulk_stops_eligible(self, agent: ModuleType) -> None:
        jobs = [
            _job("old1", "clearflow-stakeholder-parent", age_hours=30),
            _job("old2", "clearflow-obligation-grandchild", age_hours=48),
        ]
        stop = _StopRecorder()
        out = agent.run_sweep(self._input(agent), lambda: jobs, stop, NOW)
        assert out.error_type == ""
        assert out.stopped == 2
        assert out.stopped_keys == ["old1", "old2"]
        assert stop.calls == [["old1", "old2"]]

    def test_single_key_is_doubled_for_bulk_endpoint(self, agent: ModuleType) -> None:
        """Single-key Kill wedges in Terminating; the bulk API (2+ keys) is the
        only instant path — a lone zombie is passed twice (dedup-safe, proven)."""
        jobs = [_job("only", "clearflow-master-crisis", age_hours=30)]
        stop = _StopRecorder()
        out = agent.run_sweep(self._input(agent), lambda: jobs, stop, NOW)
        assert out.stopped == 1
        assert out.stopped_keys == ["only"]
        assert stop.calls == [["only", "only"]]

    def test_dry_run_never_calls_stop(self, agent: ModuleType) -> None:
        jobs = [_job("old1", "clearflow-stakeholder-parent", age_hours=30)]
        stop = _StopRecorder()
        out = agent.run_sweep(self._input(agent, dry_run=True), lambda: jobs, stop, NOW)
        assert stop.calls == []
        assert out.eligible == 1
        assert out.stopped == 0
        assert out.error_type == ""

    def test_zero_eligible_never_calls_stop(self, agent: ModuleType) -> None:
        jobs = [_job("young", "clearflow-master-crisis", age_hours=1)]
        stop = _StopRecorder()
        out = agent.run_sweep(self._input(agent), lambda: jobs, stop, NOW)
        assert stop.calls == []
        assert out.stopped == 0
        assert out.skipped_recent == 1

    def test_stop_failure_surfaces_sweep_failed(self, agent: ModuleType) -> None:
        jobs = [_job("old1", "clearflow-stakeholder-parent", age_hours=30)]
        stop = _StopRecorder(fail=True)
        out = agent.run_sweep(self._input(agent), lambda: jobs, stop, NOW)
        assert out.error_type == "SWEEP_FAILED"
        assert out.stopped == 0
        assert "boom" in out.error_message

    def test_list_failure_surfaces_sweep_failed(self, agent: ModuleType) -> None:
        def explode() -> list[dict[str, Any]]:
            raise RuntimeError("list blew up")

        out = agent.run_sweep(self._input(agent), explode, _StopRecorder(), NOW)
        assert out.error_type == "SWEEP_FAILED"
        assert out.scanned == 0

    def test_custom_threshold_and_prefix(self, agent: ModuleType) -> None:
        jobs = [
            _job("k1", "acme-case", age_hours=3),
            _job("k2", "clearflow-master-crisis", age_hours=3),
        ]
        stop = _StopRecorder()
        inp = self._input(agent, process_prefix="acme", min_age_hours=2.0)
        out = agent.run_sweep(inp, lambda: jobs, stop, NOW)
        assert out.stopped_keys == ["k1"]
        assert out.scanned == 1


class TestEntrypointNeverRaises:
    def test_main_returns_output_without_live_auth(self, agent: ModuleType) -> None:
        """dry_run + bogus folder: even if the dev machine happens to carry live
        UiPath env auth, this can only LIST a nonexistent folder — it can never
        stop anything. Whatever fails (SDK init or the list call), main() must
        return an Output, not raise."""
        result = agent.main(
            agent.Input(
                folder_key="00000000-0000-0000-0000-000000000000",
                dry_run=True,
            )
        )
        assert isinstance(result, agent.Output)
