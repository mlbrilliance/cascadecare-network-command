#!/usr/bin/env bash
# pack-solution.sh — Assemble the clearflow-solution package from canonical sources.
#
# This is the ONLY way to update maestro_case/clearflow-solution/.
# Never hand-edit the solution package. Run this before every `uip solution upload`.
#
# Usage:
#   bash scripts/pack-solution.sh          # pack with current canonical sources
#   bash scripts/pack-solution.sh --dry-run  # show what would be copied, no changes
#
# Exit codes:
#   0  success
#   1  a canonical source directory is missing
#   2  solution validation failed

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOLUTION_PKG="${REPO_ROOT}/maestro_case/clearflow-solution"
DRY_RUN=false

if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
fi

# ---------------------------------------------------------------------------
# ARTIFACTS — every project bundled into the solution, as <solution-root dirname>
# = <canonical source path>. Each is copied to the solution ROOT (flat) so the
# manifest's ProjectRelativePath (e.g. "baa-boundary-reasoner/project.uiproj")
# resolves. Cases, agents, the BPMN, the Flow, and the API workflows are all the
# same shape here: a project dir copied verbatim. They differ only in their
# canonical source root (maestro_case/, agents/, maestro_bpmn/, maestro_flow/,
# api_workflows/) — which is exactly what this map records.
#
# NOTE: the .uipx manifest + resources/solution_folder/ already hold the
# `project add` registrations (committed). This script reproduces project
# CONTENT; it does NOT re-run `project add`. To add a brand-new project, add a
# row here AND run once:
#   uip solution project add maestro_case/clearflow-solution/<dir> \
#       maestro_case/clearflow-solution/clearflow-solution.uipx
#
# Deployed SEPARATELY (NOT in this map, NOT solution-manifest projects):
#   - Coded Agents (uip codedagent): agents/claim-flow-anomaly-detector,
#       agents/forensic-self-exam-agent, agents/multi-customer-pattern-detector
#   - Coded App (uip codedapp): apps/clearflow-network-command
#     (blocked on a tenant OAuth External Application — see tasks.md)
#   - Integration Service API Workflows: api_workflows/* (14 mock external-system
#     fronts). Removed from the solution 2026-05-31 after Orchestrator install
#     Error 2005, and they don't open in the Maestro case editor — deploy via
#     Integration Service separately.
#     ROOT CAUSE FIXED 2026-05-31 (Slice 015 T016/T017): the Api packager declares
#     content/entry-points.json + content/bindings_v2.json in package-descriptor
#     but never generates them, so install saw "entry points configuration
#     missing" (2005). Each api_workflows/<slug>/ now commits both files (run
#     `uv run python scripts/gen_api_entry_points.py` to regenerate from main.json);
#     an offline pack proves all descriptor-declared files are present. Re-adding
#     them here + the live install-confirm is a tenant-session step (carried
#     forward) — to re-include, add rows below AND `uip solution project add` each.
# ---------------------------------------------------------------------------
declare -A ARTIFACTS=(
  ["clearflow-master-crisis"]="${REPO_ROOT}/maestro_case/clearflow-master-crisis"
  ["clearflow-stakeholder-parent"]="${REPO_ROOT}/maestro_case/clearflow-stakeholder-parent"
  ["clearflow-obligation-grandchild"]="${REPO_ROOT}/maestro_case/clearflow-obligation-grandchild"
  ["baa-boundary-reasoner"]="${REPO_ROOT}/agents/baa-boundary-reasoner"
  ["fiduciary-conflict-detector"]="${REPO_ROOT}/agents/fiduciary-conflict-detector"
  ["negligent-monitoring-risk-agent"]="${REPO_ROOT}/agents/negligent-monitoring-risk-agent"
  ["vector-hypothesis-agent"]="${REPO_ROOT}/agents/vector-hypothesis-agent"
  ["clearflow-ideal-incident-response"]="${REPO_ROOT}/maestro_bpmn/clearflow-ideal-incident-response"
  ["clearflow-demo-driver"]="${REPO_ROOT}/maestro_flow/clearflow-demo-driver"
)

# Stale solution-root dirs to purge before copying (artifacts removed from the
# manifest stay on disk otherwise — the copy loop only adds, never deletes).
PURGE=(
  counsel-hawthorne insurer-aurora-specialty payer-apex payer-lakeshore
  payer-summitblue payer-union-prairie provider-alpha provider-beta
  provider-delta provider-epsilon provider-gamma provider-northstar
  regulator-tn-doi vendor-nimbus
)

echo "==> CascadeCare pack-solution.sh"
echo "    Solution package: ${SOLUTION_PKG}"
echo "    Dry run: ${DRY_RUN}"
echo ""

# ---------------------------------------------------------------------------
# Validate every canonical source exists before touching the package
# ---------------------------------------------------------------------------
for name in "${!ARTIFACTS[@]}"; do
  src="${ARTIFACTS[$name]}"
  if [[ ! -d "${src}" ]]; then
    echo "ERROR: Canonical source missing: ${src}" >&2
    exit 1
  fi
  echo "  ✓ Found ${name}"
done
echo ""

# ---------------------------------------------------------------------------
# Purge stale solution-root dirs (artifacts removed from the manifest)
# ---------------------------------------------------------------------------
for name in "${PURGE[@]}"; do
  dst="${SOLUTION_PKG}/${name}"
  [[ -d "${dst}" ]] || continue
  if [[ "${DRY_RUN}" == true ]]; then
    echo "  [dry-run] Would purge stale ${dst}"
  else
    rm -rf "${dst}"
    echo "  Purged stale ${name}"
  fi
done

# ---------------------------------------------------------------------------
# Copy every canonical source into the solution package (flat at the root)
# ---------------------------------------------------------------------------
for name in "${!ARTIFACTS[@]}"; do
  src="${ARTIFACTS[$name]}"
  dst="${SOLUTION_PKG}/${name}"

  if [[ "${DRY_RUN}" == true ]]; then
    echo "  [dry-run] Would copy ${src} → ${dst}"
    continue
  fi

  rm -rf "${dst}"
  cp -r "${src}" "${dst}"
  echo "  Packed ${name} → clearflow-solution/${name}"
done

if [[ "${DRY_RUN}" == true ]]; then
  echo ""
  echo "Dry run complete. No files were modified."
  exit 0
fi

echo ""
echo "==> Sanity-checking the solution manifest..."

# There is no `uip solution validate` subcommand; the server validates on
# upload. Here we just confirm every manifest project resolves to a dir on disk.
MANIFEST="${SOLUTION_PKG}/clearflow-solution.uipx"
if command -v python3 &>/dev/null && [[ -f "${MANIFEST}" ]]; then
  python3 - "${MANIFEST}" "${SOLUTION_PKG}" <<'PY'
import json, sys, os
manifest, pkg = sys.argv[1], sys.argv[2]
projects = json.load(open(manifest)).get("Projects", [])
missing = [p["ProjectRelativePath"] for p in projects
           if not os.path.isfile(os.path.join(pkg, p["ProjectRelativePath"]))]
if missing:
    print("ERROR: manifest references missing project files:", missing, file=sys.stderr)
    sys.exit(2)
print(f"  ✓ {len(projects)} manifest projects all resolve on disk")
PY
else
  echo "  WARNING: python3 not found — skipping manifest sanity check."
fi

echo ""
echo "==> pack-solution.sh complete."
echo "    Next step: uip solution upload ${SOLUTION_PKG} --output json"
