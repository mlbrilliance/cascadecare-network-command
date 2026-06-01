#!/usr/bin/env bash
# seed_data_fabric.sh — Seed the CascadeCare Data Fabric (9 entities) and create
# the 2 Context Grounding indexes from the synthetic, IP-clean reference data in
# specs/003-uipath-native/data-model.md.
#
# Thin entry point over scripts/seed_data_fabric.py (mirrors the
# gen_api_entry_points.py build-tooling precedent — Python does the data work).
#
# Usage:
#   bash scripts/seed_data_fabric.sh                 # OFFLINE: print seed JSON
#   bash scripts/seed_data_fabric.sh --emit-json     # same, explicit
#   UIPATH_LIVE=1 bash scripts/seed_data_fabric.sh --apply   # LIVE: apply to tenant
#
# Live mode requires a prior `uip login`. No secrets live in this repo.
#
# Exit codes: 0 success · 1 bad usage · 2 generator/IP-safety failure

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GEN="${REPO_ROOT}/scripts/seed_data_fabric.py"

MODE="--emit-json"
case "${1:-}" in
  ""|--emit-json) MODE="--emit-json" ;;
  --apply)        MODE="--apply" ;;
  -h|--help)      sed -n '2,16p' "${BASH_SOURCE[0]}"; exit 0 ;;
  *)              echo "ERROR: unknown argument: $1" >&2; exit 1 ;;
esac

# Prefer `uv run` (project convention); fall back to python3 for the offline path.
if command -v uv >/dev/null 2>&1; then
  exec uv run python "${GEN}" "${MODE}"
else
  exec python3 "${GEN}" "${MODE}"
fi
