# CascadeCare Network Command

**The living case layer for healthcare financial shockwaves.**

## What This Is

When a provider goes dark, the payment network feels it first. CascadeCare Network Command demonstrates how ClearFlow Health Network -- a fictional US healthcare payment intermediary -- orchestrates a multi-customer cyber cascade as one evolving Maestro Case. The system uses three-level case nesting, agentic reasoning, and human judgment gates to manage a crisis that spans six provider customers, four payers, and five master-level goal reversals.

Built for **UiPath AgentHack 2026 Track 1** (Maestro Case). Everything runs on UiPath Automation Cloud.

## Key Features

- Three-level case nesting: master, stakeholder-parent, and obligation-grandchild cases wired via native `case-management` task type (master `caseplan.json` exists today; stakeholder-parent and obligation-grandchild planned — Slice 010)
- Five master-level reversals that reshape the crisis response in real time
- Multi-customer pattern detection across six provider organizations
- BAA boundary reasoning via UiPath Agent Builder + Claude BYO-LLM
- Context Grounding over BAA documents with Trust Layer PHI/PII guardrails
- Six provider customers managed in full parallel with materially-different BAA terms
- Action Center HITL gate for tri-party fiduciary conflict (Reversal 4)
- Hero moment: Reversal 3 fan-spawn — six grandchild cases appear simultaneously on the Maestro Case canvas

## Tech Stack

| Layer | Technologies | Status |
|-------|-------------|--------|
| Orchestration | UiPath Maestro Case (V20, 3-level nesting) | master caseplan present; parent + grandchild planned — Slice 010 |
| Process model | UiPath Maestro BPMN | planned — Slice 011 |
| Demo driver | UiPath Maestro Flow | planned — Slice 012/013 |
| Agents (reasoning) | UiPath Agent Builder × 4 (Claude BYO-LLM) | planned — Slice 008 |
| Agents (computation) | UiPath Coded Agents × 3 (Python SDK) | planned — Slice 009 |
| Mock systems | Integration Service API Workflows × 13 | planned — Slice 006 |
| Reference data | UiPath Data Fabric + Context Grounding | planned — Slice 005 |
| Governance | UiPath Trust Layer (PHI/PII detection) | planned — Slice 007 |
| HITL | UiPath Action Center | planned — Slice 010 |
| Narrative UI | UiPath Apps | planned — later slice |
| Build | Python 3.12+, uv, uip CLI | present |

## Repo Map

```
cascade_command/
  maestro_case/         # Maestro Case definitions (master caseplan.json exists; parent + grandchild planned — Slice 010)
  maestro_bpmn/         # Maestro BPMN ideal-response model (planned — Slice 011)
  maestro_flow/         # Demo Driver flow (planned — Slice 012/013)
  agents/               # Agent Builder JSON (planned — Slice 008) + Coded Agent Python packages (planned — Slice 009)
    prompts/            # Agent system prompts (Markdown, one per agent)
  api_workflows/        # Integration Service API Workflows (~13) (planned — Slice 006)
  apps/                 # UiPath Apps narrative dashboard (planned — later slice)
  src/                  # Build-time Python utilities (dev only)
  tests/                # Test suite
  specs/                # Specification files (active: specs/003-uipath-native/)
  scripts/              # pack-solution.sh; seed_data_fabric.sh (planned — Slice 005)
  knowledge/            # Immutable source-of-truth documents
  docs/                 # Architecture, usage, changelog
```

## Quickstart

> The seed, publish, and demo-run steps below describe the target end-to-end flow. They depend
> on assets that are still planned (`seed_data_fabric.sh` — Slice 005; API Workflows — Slice 006;
> agents — Slices 008/009; the Demo Driver flow — Slice 012/013). Today only the master
> `caseplan.json` and the build-time Python tooling exist.

```bash
# Install dependencies (build tooling only — no runtime Python service)
uv sync --extra dev

# Authenticate against the UiPath tenant
uv run python -m cascadecare.uipath.auth

# Seed Data Fabric with synthetic providers, payers, BAAs, claim telemetry
bash scripts/seed_data_fabric.sh

# Publish all case definitions, agents, API Workflows, and Apps to the tenant
bash scripts/pack-solution.sh
uip solution upload maestro_case/clearflow-solution/ --output json

# Start a demo run (triggers the Demo Driver flow)
uip maestro flow run clearflow-demo-driver --folder-key <FOLDER_KEY>

# Watch the cascade unfold on the Maestro Case canvas in UiPath Automation Cloud
```

## Documentation

- [Architecture](docs/architecture.md)
- [Usage & Demo Storyboard](docs/usage-examples.md)
- [Active Specification](specs/003-uipath-native/plan.md)
- [Deviations Log](DEVIATIONS.md)

## Demo Video

[Coming soon — 5-minute video, hero moment at ~2:30 (Reversal 3 subpoena fan-spawn)]

## Built with Coding Agents

This project was built using AI coding agents (Claude Code, Codex, and others). A full evidence trail — which agent built which component, key prompt excerpts, and prompt logs — will be consolidated in `CODING_AGENTS.md` and `docs/coding-agents/` (planned — Slice 016).

## IP Safety Notice

All company names, patient data, claim numbers, and regulatory citations in this project are fictional. No real healthcare organizations, patients, or legal proceedings are referenced. The `/audit-ip-safety` command enforces a forbidden-token list before every commit.

## License

Licensed under the [MIT License](LICENSE).
