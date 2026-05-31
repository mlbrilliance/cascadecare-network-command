"""UiPath Maestro Case management client.

Wraps the `uip maestro case` CLI to provide typed access to:
- Case process listing and execution
- Case instance lifecycle (get, list, pause, resume)
- Stage navigation for the five demo reversals

Auth: reads from ~/.uipath/.auth (written by `uip login`).
The caller is responsible for ensuring the token is valid before
constructing this client. Client credentials from .env work for
Orchestrator operations; Studio Web operations require interactive
user login (see DEVIATIONS.md).
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class MaestroCaseError(Exception):
    """Raised when the uip CLI returns a Failure result."""


# ---------------------------------------------------------------------------
# Domain types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CaseProcess:
    """A published Maestro Case process (template) in the tenant."""

    key: str
    name: str
    display_name: str
    folder_key: str
    version: str = "1.0.0"
    description: str = ""
    process_type: str = "CaseManagement"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CaseProcess:
        return cls(
            key=data.get("key", ""),
            name=data.get("name", ""),
            display_name=data.get("displayName", data.get("name", "")),
            folder_key=data.get("folderKey", ""),
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            process_type=data.get("processType", "CaseManagement"),
        )


@dataclass
class CaseInstance:
    """A running (or paused/completed) Maestro Case instance."""

    instance_id: str
    process_key: str
    folder_key: str = ""
    job_key: str = ""
    run_id: str = ""
    status: str = "Running"
    current_stage_id: str = ""
    current_stage_name: str = ""
    # Custom variables (mirrors caseplan.json `variables` section)
    goal: str = ""
    reversal_number: int = 0
    simulated_day: int = 0
    vector_status: str = ""
    grandchild_count: int = 0

    @classmethod
    def from_run_response(cls, data: dict[str, Any]) -> CaseInstance:
        """Construct from the `process run` response payload."""
        return cls(
            instance_id=data.get("instanceId", ""),
            process_key=data.get("processKey", ""),
            folder_key=data.get("folderKey", ""),
            job_key=data.get("jobKey", ""),
            run_id=data.get("runId", ""),
            status=data.get("status", "Running"),
        )

    @classmethod
    def from_get_response(cls, data: dict[str, Any]) -> CaseInstance:
        """Construct from the `instance get` response payload."""
        return cls(
            instance_id=data.get("id", ""),
            process_key=data.get("processKey", ""),
            folder_key=data.get("folderKey", ""),
            status=data.get("status", ""),
            current_stage_id=data.get("currentStageId", ""),
            current_stage_name=data.get("currentStageName", ""),
            goal=data.get("goal", ""),
            reversal_number=int(data.get("reversalNumber", 0)),
            simulated_day=int(data.get("simulatedDay", 0)),
            vector_status=data.get("clearFlowVectorStatus", ""),
            grandchild_count=int(data.get("grandchildCaseCount", 0)),
        )

    @classmethod
    def from_list_item(cls, data: dict[str, Any]) -> CaseInstance:
        """Construct a lightweight instance reference from a list item."""
        return cls(
            instance_id=data.get("id", ""),
            process_key=data.get("processKey", ""),
            status=data.get("status", ""),
            current_stage_name=data.get("currentStageName", ""),
        )


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class MaestroCaseClient:
    """Subprocess-backed client for `uip maestro case` operations.

    All methods invoke `uip` directly — no HTTP calls are made here.
    The client inherits auth from whatever `uip login` session is active
    in ~/.uipath/.auth.

    Parameters
    ----------
    uip_bin:
        Path to the `uip` binary. Defaults to auto-discovery via PATH.
    folder_key:
        The Orchestrator folder key that contains the case processes.
        Required for most operations. Can be overridden per-call.
    timeout:
        Subprocess timeout in seconds (default: 60).
    """

    def __init__(
        self,
        *,
        uip_bin: str | None = None,
        folder_key: str = "",
        timeout: int = 60,
    ) -> None:
        self._uip = uip_bin or self._discover_uip()
        self._folder_key = folder_key
        self._timeout = timeout

    # ------------------------------------------------------------------
    # Process operations
    # ------------------------------------------------------------------

    def list_processes(self, *, folder_key: str | None = None) -> list[CaseProcess]:
        """List published case processes in the tenant folder."""
        fkey = folder_key or self._folder_key
        result = self._run(
            ["maestro", "case", "process", "list", "--folder-key", fkey]
        )
        data = result.get("Data", [])
        if isinstance(data, list):
            return [CaseProcess.from_dict(item) for item in data]
        return []

    def run_process(
        self,
        process_key: str,
        *,
        folder_key: str | None = None,
        input_variables: dict[str, Any] | None = None,
    ) -> CaseInstance:
        """Start a new case instance for the given process key.

        Parameters
        ----------
        process_key:
            The key of the published case process (e.g. ``clearflow-crisis``).
        input_variables:
            Dictionary of case variables to pass as initial inputs.
        """
        fkey = folder_key or self._folder_key
        cmd = [
            "maestro", "case", "process", "run",
            "--process-key", process_key,
            "--folder-key", fkey,
        ]
        if input_variables:
            cmd += ["--input", json.dumps(input_variables)]
        result = self._run(cmd)
        return CaseInstance.from_run_response(result.get("Data", {}))

    # ------------------------------------------------------------------
    # Instance operations
    # ------------------------------------------------------------------

    def get_instance(
        self,
        instance_id: str,
        *,
        folder_key: str | None = None,
    ) -> CaseInstance:
        """Fetch the current state of a running case instance."""
        fkey = folder_key or self._folder_key
        result = self._run(
            ["maestro", "case", "instance", "get", instance_id, "--folder-key", fkey]
        )
        return CaseInstance.from_get_response(result.get("Data", {}))

    def list_instances(
        self,
        process_key: str,
        *,
        folder_key: str | None = None,
        status: str | None = None,
    ) -> list[CaseInstance]:
        """List instances for a given process, optionally filtered by status."""
        fkey = folder_key or self._folder_key
        cmd = [
            "maestro", "case", "instance", "list",
            "--process-key", process_key,
            "--folder-key", fkey,
        ]
        if status:
            cmd += ["--status", status]
        result = self._run(cmd)
        data = result.get("Data", [])
        if isinstance(data, list):
            return [CaseInstance.from_list_item(item) for item in data]
        return []

    def pause_instance(
        self, instance_id: str, *, folder_key: str | None = None
    ) -> None:
        """Pause a running case instance."""
        fkey = folder_key or self._folder_key
        self._run(
            ["maestro", "case", "instance", "pause", instance_id, "--folder-key", fkey]
        )

    def resume_instance(
        self, instance_id: str, *, folder_key: str | None = None
    ) -> None:
        """Resume a paused case instance."""
        fkey = folder_key or self._folder_key
        self._run(
            ["maestro", "case", "instance", "resume", instance_id, "--folder-key", fkey]
        )

    def cancel_instance(
        self, instance_id: str, *, folder_key: str | None = None
    ) -> None:
        """Cancel a case instance (irreversible)."""
        fkey = folder_key or self._folder_key
        self._run(
            ["maestro", "case", "instance", "cancel", instance_id, "--folder-key", fkey]
        )

    def get_global_variables(
        self, instance_id: str, *, folder_key: str | None = None
    ) -> dict[str, Any]:
        """Return the current global variable values for a case instance."""
        fkey = folder_key or self._folder_key
        result = self._run(
            [
                "maestro", "case", "instance", "global-variables",
                instance_id, "--folder-key", fkey,
            ]
        )
        return dict(result.get("Data", {}))

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _run(self, subcommand: list[str]) -> dict[str, Any]:
        """Run a uip subcommand and return the parsed JSON response.

        Raises
        ------
        MaestroCaseError
            When the CLI exits non-zero or the Result field is not "Success".
        """
        cmd = [self._uip, *subcommand, "--output", "json"]
        try:
            proc = subprocess.run(  # noqa: S603
                cmd,
                capture_output=True,
                text=True,
                timeout=self._timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise MaestroCaseError(
                f"uip command timed out after {self._timeout}s: {' '.join(cmd)}"
            ) from exc
        except FileNotFoundError as exc:
            raise MaestroCaseError(
                f"uip binary not found at {self._uip!r}. "
                "Run `npm install -g @uipath/cli` to install."
            ) from exc

        try:
            payload: dict[str, Any] = json.loads(proc.stdout or "{}")
        except json.JSONDecodeError as exc:
            raise MaestroCaseError(
                f"uip returned non-JSON output (exit {proc.returncode}): "
                f"{proc.stdout[:300]!r}"
            ) from exc

        result = payload.get("Result", "")
        if proc.returncode != 0 or result not in ("Success", ""):
            message = payload.get("Message", proc.stderr or "Unknown error")
            raise MaestroCaseError(message)

        return payload

    @staticmethod
    def _discover_uip() -> str:
        """Return the path to the uip binary, preferring npm-global install."""
        candidates = [
            str(Path.home() / ".npm-global" / "bin" / "uip"),
            "/usr/local/bin/uip",
            "/usr/bin/uip",
        ]
        for candidate in candidates:
            if Path(candidate).exists():
                return candidate
        found = shutil.which("uip")
        if found:
            return found
        return "uip"  # will fail at call time with a clear FileNotFoundError


# ---------------------------------------------------------------------------
# Factory — creates a client from the active uip login session
# ---------------------------------------------------------------------------


def from_active_session(*, folder_key: str = "") -> MaestroCaseClient:
    """Build a client using the uip CLI's active login session.

    The session is whatever `uip login` stored in ~/.uipath/.auth.
    If no session is active, CLI commands will return authentication errors.
    """
    return MaestroCaseClient(folder_key=folder_key)
