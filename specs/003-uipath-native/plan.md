# Implementation Plan: Slice 015 — Polish & Dress Rehearsal

**Branch**: `master` | **Date**: 2026-05-31 | **Spec**: tasks.md §Slice 015

**Input**: Slice 015 definition from `specs/003-uipath-native/tasks.md`

## Summary

Make the hero moment (Reversal 3 — the 6-grandchild/stakeholder fan-spawn) read
spectacularly on the Maestro canvas and tighten the end-to-end demo to ≤300s.
Two workstreams are **unblocked now** and need no live run: (A) canvas fan layout
in the master caseplan, and (B) UiPath Apps brand styling. A third — the live
dry-run/latency/recording verification — is **gated** on resolving the Slice 014
run blocker (package entry-points install + Maestro folder/release-key context),
which this slice must clear before the acceptance gate ("3 clean 300s dry runs")
can pass.

## Technical Context

**Language/Version**: JSON (caseplan V20 `layout` block) + Python 3.12 (build-time / Apps backend)

**Primary Dependencies**: UiPath Maestro Case V20 schema; UiPath Apps; `uip` CLI v1.1.0; `.NET 8.0.421` (pack)

**Storage**: UiPath Data Fabric (Provider/ClaimTelemetry entities); Maestro Case state (read-only for dashboard)

**Testing**: pytest (offline structure gates: layout coords, fan ordering, brand-asset presence); 3× live 300s dry runs (gated)

**Target Platform**: UiPath Automation Cloud (staging.uipath.com/hackathon26_042); solutionId 167dda12-98eb-47d9-f741-08debdbdd466

**Project Type**: UiPath Maestro Case demo system (pure-UiPath runtime)

**Performance Goals**: full R1→R5 walkthrough ≤300s wall-clock; R3 fan-spawn visibly simultaneous; dashboard read <2s; agent step latency acceptable for live narration

**Constraints**: Files ≤500 lines; zero real company names (IP safety); caseplans in `.agent-os/protected.txt` (temp-unprotect→edit→restore); knowledge/ immutable; no Co-Authored-By trailer; surgical edits (Edit over Write); secrets via .env only

**Scale/Scope**: 1 master caseplan `layout` edit (7 nodes in Regulatory Response); 1 Apps screen (branding); ≤2 new offline test cases; 1 entry-points authoring pass across the install-failing packages

## Constitution Check

*GATE: must pass before Phase 0. Re-checked after design.*

| Principle | Status | Notes |
|---|---|---|
| I. TDD-First | ✅ | Layout + brand-asset changes get offline structure tests (assert fan x-coords monotonic & distinct; assert brand tokens present) before/with the edit. No new agents/ source. |
| II. IP Safety (ZERO TOLERANCE) | ✅ | Branding uses committed fictional names (ClearFlow, Northstar, Apex…). `/audit-ip-safety` must run green pre-commit. |
| III. Externalized Agent Prompts | ✅ N/A | No prompt changes this slice. |
| IV. Surgical Edits | ✅ | Edit the `layout` block & Apps screen in place; caseplan content nodes untouched (only x/y + Apps style). |
| V. Three-Level Nesting | ✅ | Layout only repositions the existing fan; nesting structure unchanged. |
| VI. Evidence Provenance | ✅ N/A | No evidence-pack change this slice. |
| VII. Secrets via .env | ✅ | No secrets touched. |
| VIII. knowledge/ Immutable | ✅ | No writes under knowledge/. |

**Gate result: PASS.** No violations → Complexity Tracking left empty.

## Project Structure

### Documentation (this feature)

```text
specs/003-uipath-native/
├── plan.md          # This file
├── research.md      # Phase 0 — run-blocker resolution + layout/branding approach
├── tasks.md (root)  # master tracker (Slice 015 section)
└── (data-model/contracts N/A — no new entities or interfaces this slice)
```

### Source Code (repository root)

```text
maestro_case/clearflow-master-crisis/content/caseplan.json   # layout block: 6 spawn + 1 agent task in Regulatory Response
maestro_case/clearflow-solution/                             # regenerated via scripts/pack-solution.sh
apps/clearflow-network-command/                              # UiPath App — dashboard screen branding (logo/palette/typography)
tests/unit/maestro_case/test_master_fan_layout.py           # NEW — offline gate: fan coords monotonic, distinct, same row
tests/unit/apps/test_dashboard_branding.py                  # NEW — offline gate: brand tokens present on screen
api_workflows/ + maestro_bpmn/                              # entry-points definitions (run-blocker fix)
scripts/pack-solution.sh                                    # pack + manifest sanity (unchanged)
docs/demo/dry-run-log.md                                    # NEW — recorded dry-run timings + narrative notes (gated)
```

**Structure Decision**: No new project layout. Edits are confined to the master
caseplan `layout` block, the Apps dashboard screen, the install-failing package
entry-points, and two new offline test files mirroring existing `tests/unit/` shape.

## Feature Designs

### A. Canvas fan layout — master caseplan "Regulatory Response" (UNBLOCKED NOW)

The Regulatory Response stage (`Stage_JM1SVs`) holds 7 tasks: 1 BAA-analysis
agent (`tNWPCipI7`) + 6 provider spawns (`tFONj34ck` Northstar, `tP26wJSn9`
Alpha, `tP1qlCyT5` Beta, `tXX9Tu80x` Gamma, `tf3qEuV5z` Delta, `tz8z6TUHT`
Epsilon). Goal: the 6 spawns render as a **single visible horizontal fan** (one
row, evenly spaced, BAA-analysis task to the left as the trigger). Edit the
`layout` block x/y so the 6 spawns share one y, with monotonically increasing,
evenly-pitched x. Verified offline by `test_master_fan_layout.py`; visual crispness
confirmed in dry runs (gated). **Trade-off**: layout coords are advisory hints the
editor may re-flow; if Studio Web overrides on open, capture the editor's
auto-layout via download (same pattern used for the BPMN/SLA fixes) and pin that.

### B. UiPath Apps brand styling (UNBLOCKED NOW)

Apply logo, color palette, and typography to the dashboard screen in
`apps/clearflow-network-command/`. Fictional ClearFlow brand only. Verified by
`test_dashboard_branding.py` (asserts brand tokens/asset references present).
**Trade-off**: coded-app vs web-`dist/` shape mismatch noted in Slice 014 — confirm
the branding surface (screen JSON vs frontend assets) before editing.

### C. Run-blocker resolution — package entry-points + Maestro folder context (GATING)

Prerequisite for the acceptance gate. Two sub-problems:
- **Entry-points install failure**: 14 API workflows (Error 2005) + BPMN (Error
  1654) pack+publish but fail Orchestrator install for missing/invalid entry-points
  definitions. Author a valid per-package `entry-points.json` (or project.uiproj
  entry-point declaration) so install-time extraction succeeds. Research in Phase 0.
- **Maestro folder/release-key context**: `uip maestro case process run` can't map
  `CascadeCare-Core` → folder key. Resolve the Maestro-specific folder context, or
  drive R1→R5 from the Maestro UI as the documented fallback.

### D. Dry-run / latency / recording verification (GATED on C)

Three back-to-back 300s dry runs, each recorded; review for narrative tightness;
add agent cache/warm-up if latency hurts pacing. Log timings in
`docs/demo/dry-run-log.md`. Cannot start until C clears.

## Sequencing — unblocked vs gated

1. **Now (offline, parallelizable [P])**: A (fan layout) ‖ B (Apps branding) + their offline tests → commit.
2. **Gating**: C (entry-points + folder context) — must clear before D.
3. **After C**: D (dry runs, latency, recording) → acceptance gate → final commit.

If C cannot be cleared this session (next-layer authoring / human OAuth/folder
action), Slice 015 ships its **offline polish** portion and the dry-run gate
carries forward — flagged explicitly, no silent partial-complete.

## Complexity Tracking

> No Constitution Check violations — section intentionally empty.
