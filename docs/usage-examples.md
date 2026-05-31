# CascadeCare Network Command — Usage & Demo Storyboard

> **Status note.** This document describes the target end-to-end demo. Many of the assets and
> commands referenced below are still planned: `seed_data_fabric.sh` (Slice 005), Integration
> Service API Workflows (Slice 006), Trust Layer + BYO-LLM registration (Slice 007), Agent
> Builder agents (Slice 008), Coded Agents (Slice 009), the stakeholder-parent and
> obligation-grandchild caseplans + Action Center HITL gate (Slice 010), the Maestro Flow Demo
> Driver (Slice 012/013), the UiPath Apps dashboard (later slice), and the coding-agent evidence
> pack (`CODING_AGENTS.md`, `docs/coding-agents/`, Slice 016). Today only the master
> `caseplan.json` and build-time Python tooling exist.

## Prerequisites

1. UiPath Automation Cloud tenant with Maestro Case, Maestro Flow, Agent Builder, Data Fabric, Trust Layer, Action Center, and Integration Service enabled
2. External app `e7145523-3cdd-40f1-b2f2-c1b105aa217f` granted scopes: Studio Web (publish), Maestro (full), Integration Service, Data Fabric, UiPath Apps, Action Center
3. Claude BYO-LLM connection registered: `uip llm-configuration byo-connections`
4. `uv sync --extra dev` — installs build-time tooling
5. `bash scripts/seed_data_fabric.sh` — seeds all synthetic Data Fabric entities
6. `bash scripts/pack-solution.sh && uip solution upload maestro_case/clearflow-solution/ --output json` — publishes the solution

---

## 5-Minute Demo Storyboard (300 seconds)

The demo runs on **UiPath Automation Cloud** only. The operator has three browser windows open:
- **Window A**: Maestro Case canvas (`clearflow-master-crisis`)
- **Window B**: UiPath Studio Web (showing the Maestro Flow Demo Driver and BPMN model)
- **Window C**: UiPath Apps `clearflow-network-command` (narrative dashboard, supporting cuts only)

| Wall-clock | Sim Day | Beat | Camera | UiPath Surface |
|---|---|---|---|---|
| 0–20s | — | Cold open | Title card; voiceover: "ClearFlow Health Network, May 2026" | Window B: Maestro BPMN ideal-response model briefly visible |
| 20s | Day 1 | **R1: Multi-customer correlation** | Master case opens; "Multi-Customer Investigation" stage activates | Window A: Maestro Case canvas — Claim Anomaly + Pattern Detector Coded Agent tasks fire |
| 45s | Day 3 | Child event: PHI exfiltration | Trust Layer alert on PHI-laden LLM call; Business Associate Exposure parent spawns | Window A: parent case card appears on canvas |
| 70s | Day 5 | **R2: ClearFlow cleared, Nimbus revealed** | Vector Hypothesis Agent Builder panel: visible reasoning chain | Window A: agent reasoning trace inline; Nimbus vendor parent case spawns |
| 100s | Day 14 | Child event: provider liquidity stress | Northstar parent escalates; Payment Continuity grandchild spawns | Window A: grandchild tile appears under Northstar parent |
| **150s** | **Day 30** | **R3 — HERO: Subpoena cascade** | **TN DOI subpoena event → 6 stakeholder-parent cases fan-spawn simultaneously in "Regulatory Response" stage. Camera holds 8–10s.** | **Window A: Maestro Case canvas. Six case-management tiles appear in a horizontal fan. Three-level hierarchy visible in a single frame.** |
| 200s | Day 45 | **R4: Tri-party HITL gate** | Action Center "TRI-PARTY APPROVAL" task appears; Fiduciary Conflict Detector reasoning visible | Window A: Action Center notification; switch to Action Center task view |
| 260s | Day 90 | **R5: Litigation cascade** | ClearFlow named co-defendant; Negligent Monitoring Risk Agent fires; privilege flags reshuffle on grandchild cases | Window A: grandchild case privilege-flag toggles visible (attorney-client → work-product) |
| 280–300s | — | Outro | Brief cut to Apps dashboard showing reversal timeline and cascade tree | Window C: Apps narrative dashboard; presenter voiceover wrap |

---

## Starting the Demo

```bash
# Trigger the Demo Driver flow (from build machine)
uip maestro flow run clearflow-demo-driver \
  --folder-key <FOLDER_KEY> \
  --output json
```

The Demo Driver fires 7 API Workflow calls at compressed intervals (t+10s through t+210s), each injecting an event that the Maestro Triggers pick up and route to the appropriate agent task or case-management spawn.

### Manual event injection (testing individual beats)

If you want to fire a specific reversal without running the full Demo Driver:

```bash
# Fire the TN DOI subpoena event (Reversal 3 / hero moment)
uip integration-service api-workflow run regulator-tn-doi \
  --input '{"event_type": "subpoena", "scope": "all_providers", "day": 30}' \
  --output json

# Fire the payer demand event (Reversal 4 setup)
uip integration-service api-workflow run payer-apex \
  --input '{"event_type": "data_access_demand", "day": 45}' \
  --output json
```

---

## Verifying a Clean State

Before a demo run:

```bash
# Check master case is in expected state
uip maestro case instance list --process clearflow-master-crisis --output json

# Verify Data Fabric entities are seeded
uip data-fabric entity list --entity-type Provider --output json | jq '.[].name'
# Expected: Northstar Regional Health, Provider Alpha, Provider Beta,
#           Provider Gamma, Provider Delta, Provider Epsilon

# Confirm Trust Layer policy is active
uip trust-layer policy list --output json

# Confirm BYO-LLM connection
uip llm-configuration list --output json | jq '.[].name'
# Expected: anthropic-claude (or your registered connection name)
```

---

## Validation Checks (per-slice, after every publish)

1. **Schema validation**: `uip maestro case validate maestro_case/clearflow-master-crisis/content/caseplan.json --output json` — zero errors
2. **Solution validation**: `uip solution validate maestro_case/clearflow-solution/ --output json` — passes
3. **Solution publish**: `uip solution upload maestro_case/clearflow-solution/ --output json` — returns Designer URL
4. **Smoke run**: `uip maestro case process run clearflow-master-crisis <folder-key> --inputs '{}'` — instance starts; `uip maestro case instance get <id>` shows expected stage
5. **Demo Driver dry run**: Trigger `clearflow-demo-driver`; observe master case advancing R1→R5; capture canvas screenshots at R3 hero moment
6. **HITL test**: At R4, confirm Action Center task appears with priority "Critical" and tri-party form
7. **Trust Layer verification**: Send PHI-laden test input through BAA Boundary Reasoner; confirm detection fires
8. **Full 300s rehearsal**: Record wall-clock end-to-end; review for narrative tightness
9. **IP safety audit**: `/audit-ip-safety` passes (zero forbidden tokens)

---

## Evidence Pack (Coding Agent Documentation) (planned — Slice 016)

After the demo is complete, the evidence pack for the coding-agent bonus is assembled at:

```bash
# Collect coding agent evidence
ls docs/coding-agents/     # per-component docs
ls docs/prompt-logs/       # sanitized prompt transcripts
ls docs/coding-agents/screenshots/  # visual evidence
cat CODING_AGENTS.md       # canonical reference
```

See `CODING_AGENTS.md` for the full list of components built by each coding agent.

---

## Reset

To reset the demo to initial state, terminate the running master case instance and re-run seed + publish:

```bash
# Terminate all running instances
uip maestro case instance list --process clearflow-master-crisis --output json \
  | jq -r '.[].id' \
  | xargs -I {} uip maestro case instance stop {} --output json

# Re-seed Data Fabric (idempotent)
bash scripts/seed_data_fabric.sh

# Re-publish and start fresh
bash scripts/pack-solution.sh
uip solution upload maestro_case/clearflow-solution/ --output json
```
