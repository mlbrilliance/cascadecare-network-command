# Built with Coding Agents — CascadeCare Network Command

> Canonical authorship reference for the AgentHack 2026 **coding-agent bonus**.
> The full per-type evidence pages live in [`docs/coding-agents/`](docs/coding-agents/).

## The bonus triad

**(a) Which coding agent** — **Claude Code** (Anthropic's CLI), running Claude Opus/Sonnet,
authored 100% of this repository. Every UiPath artifact, every test, every spec, and every
build script was written by Claude Code driving the UiPath `uip` CLI and the official
`uipath-*` authoring skills.

**(b) How it contributed** — Claude Code ran the entire build as a sequence of test-gated
slices (004 → 017) under a spec-kit workflow (`/speckit.plan → analyze → tasks → implement`),
a Spec-Gate-per-function discipline, and a mandatory IP-safety audit on every commit. For each
UiPath component it: read the authoritative `uipath-*` skill, authored the artifact to the V20 /
CNCF / Agent-Builder contract, wrote an offline structure test **first** (TDD), and verified
against the real `uip` CLI (e.g. `uip api-workflow validate`, `uip maestro bpmn validate`,
offline `uip solution pack` probes). Diagnoses were empirical, not guessed — e.g. Orchestrator
**Error 2005** was root-caused by packing an Api project offline and inspecting the generated
`package-descriptor.json` against the nupkg contents (see [api-workflows](docs/coding-agents/api-workflows.md)).

**(c) Verifiable evidence** —
- [`docs/changelog.md`](docs/changelog.md) — the durable per-slice build narrative.
- [`agents/prompts/*.md`](agents/prompts/) — 7 committed agent prompt templates (never inlined).
- [`specs/003-uipath-native/`](specs/003-uipath-native/) — the spec-kit authoring trail
  (`plan.md`, `research.md`, `slice-0NN-tasks.md`).
- The 27 UiPath artifacts themselves + their offline test gates under [`tests/`](tests/).
- [`docs/prompt-logs/`](docs/prompt-logs/) and [`docs/coding-agents/screenshots/`](docs/coding-agents/screenshots/)
  — session-capture channels (status tracked per their READMEs).

## Authorship table — 27 UiPath artifacts

| # | Artifact | Type | Slice | Authoring agent | Evidence |
|---|---|---|---|---|---|
| 1 | `clearflow-master-crisis` | Maestro **Case** (V20) | 010 | Claude Code + `uipath-maestro-case` | [cases](docs/coding-agents/cases.md) |
| 2 | `clearflow-stakeholder-parent` | Maestro Case (V20) | 010 | Claude Code + `uipath-maestro-case` | [cases](docs/coding-agents/cases.md) |
| 3 | `clearflow-obligation-grandchild` | Maestro Case (V20) | 010 | Claude Code + `uipath-maestro-case` | [cases](docs/coding-agents/cases.md) |
| 4 | `vector-hypothesis-agent` | **Agent Builder** (low-code, Claude BYO-LLM) | 008 | Claude Code + `uipath-agents` | [agents-lowcode](docs/coding-agents/agents-lowcode.md) |
| 5 | `baa-boundary-reasoner` | Agent Builder (+ Context Grounding) | 008 | Claude Code + `uipath-agents` | [agents-lowcode](docs/coding-agents/agents-lowcode.md) |
| 6 | `fiduciary-conflict-detector` | Agent Builder | 008 | Claude Code + `uipath-agents` | [agents-lowcode](docs/coding-agents/agents-lowcode.md) |
| 7 | `negligent-monitoring-risk-agent` | Agent Builder | 008 | Claude Code + `uipath-agents` | [agents-lowcode](docs/coding-agents/agents-lowcode.md) |
| 8 | `claim-flow-anomaly-detector` | **Coded Agent** (Python SDK) | 009 | Claude Code + `uipath-coded-apps` (TDD) | [agents-coded](docs/coding-agents/agents-coded.md) |
| 9 | `multi-customer-pattern-detector` | Coded Agent | 009 | Claude Code + `uipath-coded-apps` (TDD) | [agents-coded](docs/coding-agents/agents-coded.md) |
| 10 | `forensic-self-exam-agent` | Coded Agent | 009 | Claude Code + `uipath-coded-apps` (TDD) | [agents-coded](docs/coding-agents/agents-coded.md) |
| 11–24 | `api_workflows/*` (14 slugs) | **API Workflow** (`Type:"Api"`, CNCF Serverless 1.0.0) | 006 / 015 | Claude Code + `uipath-api-workflow` | [api-workflows](docs/coding-agents/api-workflows.md) |
| 25 | `clearflow-ideal-incident-response` | Maestro **BPMN** | 011 | Claude Code + `uipath-maestro-bpmn` | [bpmn](docs/coding-agents/bpmn.md) |
| 26 | `clearflow-demo-driver` | Maestro **Flow** (Demo Driver) | 012 | Claude Code + `uipath-maestro-flow` | [flow](docs/coding-agents/flow.md) |
| 27 | `clearflow-network-command` | UiPath **Apps** (narrative dashboard) | 013 / 015 | Claude Code + `uipath-coded-apps` | [apps](docs/coding-agents/apps.md) |

Plus the connective tissue Claude Code authored: the `clearflow-solution` `.uipx` packaging
(`scripts/pack-solution.sh`), Data Fabric entity schemas (specified in
`specs/003-uipath-native/data-model.md`), Context Grounding index resources, the 470+ offline
test gates, and this evidence set.

## Build methodology (how a slice was driven)

1. `/speckit.plan` → `/speckit.analyze` → `/speckit.tasks` from the slice in
   `specs/003-uipath-native/tasks.md`.
2. **Spec Gate** per function — purpose / inputs / outputs / edge cases before any code.
3. **TDD** — offline structure test authored RED before the artifact (enforced by a pre-write
   hook for `agents/`, `shim/`, `mocks/`).
4. Author against the authoritative `uipath-*` skill; verify with the real `uip` CLI offline.
5. `/audit-ip-safety` (zero real-company tokens) + `uv run pytest` green before commit.
6. `/thermo-nuclear-code-quality-review` ↔ `/improve-codebase-architecture` on the slice diff.

## IP safety

Every artifact and every line of evidence uses only the fictional cast (ClearFlow, Northstar,
Apex, Nimbus, Aurora Specialty, …). Zero real healthcare-company tokens — enforced by
`/audit-ip-safety` on each commit.
