"""Case-Job Janitor — UiPath Coded Function Agent (Slice 023 ops utility).

Why this exists: on this tenant a completed Maestro case instance NEVER flips its
Orchestrator job to Successful — the job row shows "Running" forever (proven
2026-06-12: masters whose instances completed 1 and 3 days earlier still showed
Running jobs; `jobs history` records Pending→Running and no terminal transition).
Job state is runtime-owned, so no API can mark them Successful; the best external
transition is Stopped via the BULK StopJobs endpoint (2+ keys — a single-key Kill
wedges in Terminating, SoftStop wedges in Stopping). Killing the job shell does
not touch the case instance: Maestro Monitoring keeps showing Completed
(verified on 27 jobs).

Deterministic core: ``select_zombies`` / ``run_sweep`` — given Running/Pending
jobs, pick the ones matching our case-definition prefix that are older than the
safety threshold (code default 24 h; the hourly trigger passes a lower value for
demo hygiene) and bulk-stop them. Age is taken from StartTime, falling back to
CreationTime so Maestro "Agentic process" / Pending jobs (which can have an empty
StartTime) are aged correctly instead of being skipped forever. Both are fully
testable without UiPath auth — the module imports only stdlib + pydantic at module
level; every UiPath import lives inside a function body.

Deployed standalone next to the other coded agents and run on an hourly
Orchestrator time trigger, it keeps the Jobs view free of zombie "Running" rows
throughout the AgentHack judging window. The manual sweep (DEMO-RUNBOOK A6)
remains the instant-cleanup tool right after a test run.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from pydantic import BaseModel, Field

# CascadeCare-v110 deployment folder (DEMO-RUNBOOK reference table).
DEFAULT_FOLDER_KEY = "de7b7c18-d743-4c8c-b555-9bd3b96fe524"

_PAGE_SIZE = 100
# Runaway guard: 10 pages x 100 jobs is far beyond any real zombie population.
_MAX_PAGES = 10


class Input(BaseModel):
    """Sweep scope and safety controls."""

    folder_key: str = Field(
        default=DEFAULT_FOLDER_KEY,
        description="Orchestrator folder to sweep (GUID).",
    )
    process_prefix: str = Field(
        default="clearflow",
        description="Only jobs whose process name starts with this are considered.",
    )
    min_age_hours: float = Field(
        default=24.0,
        description="Safety threshold: jobs younger than this are never touched "
        "(protects live demo walks and same-day HITL waits).",
    )
    dry_run: bool = Field(
        default=False,
        description="Report eligible zombies without stopping anything.",
    )


class Output(BaseModel):
    """Sweep report (entrypoint never raises; errors land here)."""

    scanned: int = 0
    eligible: int = 0
    stopped: int = 0
    stopped_keys: list[str] = []
    skipped_recent: int = 0
    error_type: str = ""
    error_message: str = ""


def _parse_start(value: Any) -> datetime | None:
    """Parse a job StartTime into an aware datetime; None when unusable.

    A job whose age cannot be established is NEVER eligible — we only stop what
    we can prove is old.
    """
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def select_zombies(
    jobs: list[dict[str, Any]],
    prefix: str,
    min_age_hours: float,
    now: datetime,
) -> tuple[list[str], int, int]:
    """Pick stoppable zombies from Running jobs.

    Returns (eligible_keys, scanned, skipped_recent) where ``scanned`` counts
    prefix-matching jobs and ``skipped_recent`` those protected by the age
    threshold (including unparseable start times).
    """
    eligible: list[str] = []
    scanned = 0
    skipped_recent = 0
    for job in jobs:
        if not str(job.get("process_name", "")).startswith(prefix):
            continue
        scanned += 1
        # Age basis: StartTime, falling back to CreationTime. Maestro
        # "Agentic process" / Pending jobs can carry an empty StartTime; without
        # the fallback those would be treated as unknowable-age and never swept.
        started = _parse_start(job.get("start_time")) or _parse_start(job.get("creation_time"))
        if started is None or (now - started).total_seconds() < min_age_hours * 3600:
            skipped_recent += 1
            continue
        eligible.append(str(job.get("key", "")))
    return eligible, scanned, skipped_recent


def run_sweep(
    inp: Input,
    list_jobs: Callable[[], list[dict[str, Any]]],
    stop_jobs: Callable[[list[str]], None],
    now: datetime,
) -> Output:
    """Orchestrate one sweep over injected list/stop callables (testable core)."""
    try:
        jobs = list_jobs()
    except Exception as exc:
        return Output(error_type="SWEEP_FAILED", error_message=str(exc))

    eligible, scanned, skipped_recent = select_zombies(
        jobs, inp.process_prefix, inp.min_age_hours, now
    )
    out = Output(scanned=scanned, eligible=len(eligible), skipped_recent=skipped_recent)
    if inp.dry_run or not eligible:
        return out

    # The bulk endpoint (2+ keys) is the only transition that lands on Stopped
    # instantly; a lone key is passed twice (the API dedupes — proven live).
    payload = eligible if len(eligible) > 1 else [eligible[0], eligible[0]]
    try:
        stop_jobs(payload)
    except Exception as exc:
        out.error_type = "SWEEP_FAILED"
        out.error_message = str(exc)
        return out
    out.stopped = len(eligible)
    out.stopped_keys = eligible
    return out


def main(input: Input) -> Output:  # noqa: A002 — UiPath entrypoint signature uses `input`.
    """UiPath Coded Function entrypoint (declared in uipath.json `functions`)."""
    try:
        from uipath.platform import UiPath  # noqa: PLC0415 — lazy, auth-gated.

        sdk = UiPath()
    except Exception as exc:
        return Output(error_type="AUTH_FAILED", error_message=str(exc))

    def list_jobs() -> list[dict[str, Any]]:
        collected: list[dict[str, Any]] = []
        for page in range(_MAX_PAGES):
            result = sdk.jobs.list(
                folder_key=input.folder_key,
                filter="State eq 'Running' or State eq 'Pending'",
                skip=page * _PAGE_SIZE,
                top=_PAGE_SIZE,
            )
            items = list(getattr(result, "items", None) or [])
            for job in items:
                collected.append(
                    {
                        "key": getattr(job, "key", None) or getattr(job, "Key", ""),
                        "process_name": getattr(job, "release_name", None)
                        or getattr(job, "process_name", None)
                        or getattr(job, "ReleaseName", "")
                        or "",
                        "start_time": getattr(job, "start_time", None)
                        or getattr(job, "StartTime", None),
                        "creation_time": getattr(job, "creation_time", None)
                        or getattr(job, "CreationTime", None),
                    }
                )
            if len(items) < _PAGE_SIZE:
                break
        return collected

    def stop_jobs(keys: list[str]) -> None:
        sdk.jobs.stop(job_keys=keys, strategy="Kill", folder_key=input.folder_key)

    try:
        return run_sweep(input, list_jobs, stop_jobs, datetime.now(timezone.utc))
    except Exception as exc:  # entrypoint must not leak exceptions.
        return Output(error_type="SWEEP_FAILED", error_message=str(exc))
