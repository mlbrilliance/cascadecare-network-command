#!/usr/bin/env bash
# cleanup_deployments.sh — Uninstall the stale CascadeCare solution deployments,
# leaving exactly one canonical deployment (CascadeCare-Full) on the tenant.
#
# WHY THIS EXISTS — Slices 014–018 left up to four throwaway deployments
# (CascadeCare-Core / -Smoke / -Live / -Demo) alongside the canonical
# CascadeCare-Full. Judges and our own smoke runs need exactly ONE unambiguous
# deployment. This script removes the stale set and never touches the keeper.
#
# SAFETY MODEL (defense in depth):
#   1. KEEP_LIST is sacrosanct — a name in KEEP_LIST is NEVER uninstalled, even
#      if someone adds it to STALE_SET by mistake.
#   2. Refuses to mutate without an explicit --confirm flag.
#   3. --dry-run (the default behaviour without --confirm) prints the plan only.
#   4. Only uninstalls deployments that BOTH exist on the tenant AND are in
#      STALE_SET — so it is idempotent and safe to re-run.
#   5. No secrets in this file. Auth comes from a prior `uip login` (env/token).
#
# Usage:
#   bash scripts/cleanup_deployments.sh                # dry-run: print the plan
#   bash scripts/cleanup_deployments.sh --dry-run      # same, explicit
#   bash scripts/cleanup_deployments.sh --confirm      # actually uninstall
#
# Exit codes:
#   0  success (plan printed, or all stale deployments uninstalled)
#   1  bad usage
#   2  a uip command failed

set -euo pipefail

# --- The one deployment that must survive. NEVER add throwaway names here. ----
KEEP_LIST=(
  "CascadeCare-Full"
)

# --- The throwaway deployments to remove. -------------------------------------
STALE_SET=(
  "CascadeCare-Core"
  "CascadeCare-Smoke"
  "CascadeCare-Live"
  "CascadeCare-Demo"
)

CONFIRM=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --confirm) CONFIRM=true; shift ;;
    --dry-run) DRY_RUN=true; shift ;;
    -h|--help)
      sed -n '2,33p' "${BASH_SOURCE[0]}"
      exit 0
      ;;
    *) echo "ERROR: unknown argument: $1" >&2; exit 1 ;;
  esac
done

# --- Guard: a KEEP_LIST name must never appear in STALE_SET. ------------------
for keep in "${KEEP_LIST[@]}"; do
  for stale in "${STALE_SET[@]}"; do
    if [[ "$keep" == "$stale" ]]; then
      echo "FATAL: '$keep' is in both KEEP_LIST and STALE_SET — refusing to run." >&2
      exit 1
    fi
  done
done

is_kept() {
  local name="$1"
  for keep in "${KEEP_LIST[@]}"; do
    [[ "$name" == "$keep" ]] && return 0
  done
  return 1
}

echo "==> CascadeCare deployment cleanup"
echo "    KEEP : ${KEEP_LIST[*]}"
echo "    STALE: ${STALE_SET[*]}"
echo

if [[ "$CONFIRM" != true ]]; then
  echo "DRY-RUN (no --confirm). Would attempt to uninstall, if present:"
  for name in "${STALE_SET[@]}"; do
    if is_kept "$name"; then
      echo "    SKIP (keep-list)  $name"
    else
      echo "    uninstall         $name"
    fi
  done
  echo
  echo "Re-run with --confirm to execute. CascadeCare-Full is never touched."
  exit 0
fi

# --- Live mode: enumerate existing deployments, then uninstall the stale ------
echo "==> Listing current deployments..."
if ! existing_json="$(uip solution deploy list --output json 2>/dev/null)"; then
  echo "ERROR: 'uip solution deploy list' failed — run 'uip login' first." >&2
  exit 2
fi

# Extract deployment names (best-effort across list/{Deployments:[]} shapes).
existing_names="$(
  printf '%s' "$existing_json" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
items = data.get("Deployments", data) if isinstance(data, dict) else data
if isinstance(items, list):
    for it in items:
        if isinstance(it, dict):
            name = it.get("DeploymentName") or it.get("Name") or it.get("name")
            if name:
                print(name)
'
)"

echo "    Found: $(printf '%s' "$existing_names" | paste -sd' ' -)"
echo

rc=0
for name in "${STALE_SET[@]}"; do
  if is_kept "$name"; then
    echo "    SKIP (keep-list)  $name"
    continue
  fi
  if ! printf '%s\n' "$existing_names" | grep -qx "$name"; then
    echo "    absent (skip)     $name"
    continue
  fi
  echo "    uninstalling      $name ..."
  if uip solution deploy uninstall "$name" --output json; then
    echo "    ✓ uninstalled     $name"
  else
    echo "    ✗ FAILED          $name" >&2
    rc=2
  fi
done

echo
echo "==> Cleanup complete. CascadeCare-Full left intact."
exit "$rc"
