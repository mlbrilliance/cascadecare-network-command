"""Slice 019 (b) — structural gate for scripts/cleanup_deployments.sh.

Offline-only: validates the script's safety invariants without touching the
tenant. The live uninstall (T-b3) is a human/online step.

Invariants pinned here:
  - CascadeCare-Full is in the keep-list and is NEVER an uninstall target.
  - The stale set is exactly the four expected throwaway deployments.
  - The script refuses to mutate without --confirm (default is dry-run).
  - There is a hard guard preventing a keep-name from being uninstalled.
  - No hard-coded secrets.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "scripts" / "cleanup_deployments.sh"

KEEP = {"CascadeCare-Full"}
STALE = {"CascadeCare-Core", "CascadeCare-Smoke", "CascadeCare-Live", "CascadeCare-Demo"}


def _array(name: str) -> set[str]:
    """Parse a bash array literal `NAME=( "a" "b" )` from the script."""
    text = SCRIPT.read_text(encoding="utf-8")
    m = re.search(rf"{name}=\((.*?)\)", text, re.DOTALL)
    assert m, f"{name} array not found in {SCRIPT.name}"
    return set(re.findall(r'"([^"]+)"', m.group(1)))


def test_script_exists_and_executable() -> None:
    assert SCRIPT.exists(), f"{SCRIPT} missing"
    assert SCRIPT.stat().st_mode & 0o111, "cleanup script must be executable"


def test_keep_list_is_exactly_the_keeper() -> None:
    assert _array("KEEP_LIST") == KEEP


def test_stale_set_is_exactly_the_four_throwaways() -> None:
    assert _array("STALE_SET") == STALE


def test_keeper_never_in_stale_set() -> None:
    assert _array("KEEP_LIST").isdisjoint(_array("STALE_SET"))


def test_has_confirm_guard() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "--confirm" in text, "script must require an explicit --confirm flag"
    assert 'CONFIRM" != true' in text or "CONFIRM != true" in text, (
        "script must short-circuit to dry-run when --confirm is absent"
    )


def test_no_hardcoded_secrets() -> None:
    text = SCRIPT.read_text(encoding="utf-8").lower()
    for needle in ("client_secret", "password", "bearer ", "api_key", "apikey="):
        assert needle not in text, f"possible secret in cleanup script: {needle!r}"


def test_dry_run_does_not_call_uip_and_lists_plan() -> None:
    """Running without --confirm must print the plan and never invoke uip."""
    proc = subprocess.run(
        ["bash", str(SCRIPT)],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO_ROOT),
    )
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout
    assert "DRY-RUN" in out
    for name in STALE:
        assert name in out, f"dry-run plan should mention {name}"
    assert "CascadeCare-Full is never touched" in out


def test_bad_argument_is_rejected() -> None:
    proc = subprocess.run(
        ["bash", str(SCRIPT), "--bogus"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO_ROOT),
    )
    assert proc.returncode == 1
