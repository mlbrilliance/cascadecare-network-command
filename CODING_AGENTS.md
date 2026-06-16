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
- [`agents/prompts/*.md`](agents/prompts/) — 9 committed agent prompt templates (never inlined).
- [`specs/003-uipath-native/`](specs/003-uipath-native/) — the spec-kit authoring trail
  (`plan.md`, `research.md`, `slice-0NN-tasks.md`).
- The 27 UiPath artifacts themselves + their offline test gates under [`tests/`](tests/).
- [`docs/prompt-logs/`](docs/prompt-logs/) and [`docs/coding-agents/screenshots/`](docs/coding-agents/screenshots/)
  — session-capture channels (status tracked per their READMEs).

## Authorship table — 37 UiPath artifacts

| # | Artifact(s) | Type | Authoring agent + skill | Evidence |
|---|---|---|---|---|
| 1–3 | `clearflow-master-crisis`, `clearflow-stakeholder-parent`, `clearflow-obligation-grandchild` | Maestro **Case** (V20, 3-level nesting) | Claude Code + `uipath-maestro-case` | [cases](docs/coding-agents/cases.md) |
| 4 | `baa-boundary-reasoner` (+ Context Grounding `BAA-corpus`) | **Agent Builder** (Claude Sonnet 4.6 BYO-LLM) | Claude Code + `uipath-agents` | [agents-lowcode](docs/coding-agents/agents-lowcode.md) |
| 5 | `vector-hypothesis-agent` | Agent Builder | Claude Code + `uipath-agents` | [agents-lowcode](docs/coding-agents/agents-lowcode.md) |
| 6 | `fiduciary-conflict-detector` | Agent Builder | Claude Code + `uipath-agents` | [agents-lowcode](docs/coding-agents/agents-lowcode.md) |
| 7 | `negligent-monitoring-risk-agent` | Agent Builder | Claude Code + `uipath-agents` | [agents-lowcode](docs/coding-agents/agents-lowcode.md) |
| 8 | `assess-claim-disruption` | Agent Builder | Claude Code + `uipath-agents` | [agents-lowcode](docs/coding-agents/agents-lowcode.md) |
| 9 | `classify-obligation` | Agent Builder | Claude Code + `uipath-agents` | [agents-lowcode](docs/coding-agents/agents-lowcode.md) |
| 10 | `forensic-self-exam-agent-langgraph` (**LIVE**) | **Coded · LangGraph** `StateGraph` (`uipath-langchain`) | Claude Code + `uipath-agents` (TDD) | [agents-coded](docs/coding-agents/agents-coded.md) |
| 11 | `claim-flow-anomaly-detector` | **Coded Agent** (Python SDK) | Claude Code + `uipath-agents` (TDD) | [agents-coded](docs/coding-agents/agents-coded.md) |
| 12 | `multi-customer-pattern-detector` | Coded Agent | Claude Code + `uipath-agents` (TDD) | [agents-coded](docs/coding-agents/agents-coded.md) |
| 13 | `forensic-self-exam-agent` (original; superseded by #10) | Coded Agent | Claude Code + `uipath-agents` (TDD) | [agents-coded](docs/coding-agents/agents-coded.md) |
| 14 | `case-job-janitor` (ops; hourly Orchestrator trigger) | Coded Agent | Claude Code + `uipath-agents` (TDD) | [agents-coded](docs/coding-agents/agents-coded.md) |
| 15–33 | `api_workflows/*` (**19 slugs**, incl. 3 ViVE Healthcare bridges) | **API Workflow** (`Type:"Api"`, CNCF Serverless 1.0.0) | Claude Code + `uipath-api-workflow` | [api-workflows](docs/coding-agents/api-workflows.md) |
| 34 | `clearflow-ideal-incident-response` | Maestro **BPMN** | Claude Code + `uipath-maestro-bpmn` | [bpmn](docs/coding-agents/bpmn.md) |
| 35 | `case-closed-notification` | Maestro BPMN | Claude Code + `uipath-maestro-bpmn` | [bpmn](docs/coding-agents/bpmn.md) |
| 36 | `clearflow-demo-driver` | Maestro **Flow** (Demo Driver) | Claude Code + `uipath-maestro-flow` | [flow](docs/coding-agents/flow.md) |
| 37 | `clearflow-network-command` | UiPath **Apps** (Coded Web App dashboard) | Claude Code + `uipath-coded-apps` | [apps](docs/coding-agents/apps.md) |

Plus the connective tissue Claude Code authored: the `clearflow-solution` `.uipx` packaging
(`scripts/pack-solution.sh`), Data Fabric entity schemas + seeding (`scripts/seed_data_fabric.py`),
Context Grounding index resources + corpus generation (`scripts/gen_cg_corpus.py`), the **680**
offline test gates, and this evidence set.

**Criterion-3 evidence (exception handling, authored test-first).** The forensic agent's
`enrich_node` was hardened by Claude Code under a red→green TDD cycle: a failing test was written
first (forcing the LLM-Gateway call to raise) proving the error was silently swallowed, then the fix
populated `error_type`/`error_message` while preserving deterministic routing — see
[`tests/agents/test_forensic_langgraph.py`](tests/agents/test_forensic_langgraph.py) and the
defense-in-depth layers in [README "Exception, Failure & Edge-Case Handling"](README.md#exception-failure--edge-case-handling-criterion-3).

## Above and beyond — open-source contribution (`Maestro Case Kit`)

Claude Code didn't only build the demo — it extracted the project's hardest-won, **undocumented
UiPath Maestro Case / Data Fabric / Action Center** discoveries into a standalone, installable,
open-source toolkit at [`tooling/maestro-case-kit/`](tooling/maestro-case-kit/) that UiPath could
dogfood directly. One define-once Python source ships as **four agent-native artifacts** over a
shared tool registry — a `maestro-case` CLI, a dependency-free MCP server, a Claude Code skill, and
an OpenClaw skill — all **offline and credential-free** (no UiPath login):

| Footgun (hit live in this build) | Tool |
|---|---|
| Cryptic, un-Googleable error codes (`400300`, `160009`, …) | `maestro-case explain <code>` → proven cause + fix |
| Inert caseplan edits (stale `.bpmn`, dropped start event) | `maestro-case lint <dir>` — validated clean on all 3 live caseplans |
| `=datafabric.qem:` in spawn inputs → runtime `400300` | `maestro-case check-spawn <dir>` |
| Data Fabric silent field-drop / reserved `id` | `maestro-case check-df <spec>` |
| `uip case`/`uip flow` without the `maestro` prefix (UiPath's own skills had it) | `maestro-case check-cli <dir>` |

Authored test-first like the rest of the build (64 toolkit tests wired into the repo
`uv run pytest` gate; 747 total pass, `mypy` clean, IP-safe). Each knowledge entry is
version-stamped and self-deprecates when UiPath ships a fix, behind an automated schema +
IP-safety contribution gate. We even hit this footgun in UiPath's *own* official skills — the
`uip maestro` CLI namespace (issues #333/#337) — now **fixed upstream** on UiPath's `main`; rather
than a no-op PR we shipped it as the toolkit's `check-cli` regression guard (verified findings in
[`docs/submission/CONTRIBUTE-BACK-PR.md`](docs/submission/CONTRIBUTE-BACK-PR.md)). Built via `/ce-ideate → /ce-brainstorm → /ce-work`; a spike
proved the `printing-press` generator only wraps external APIs, so it is a define-once Python source —
**not** printing-press-generated — and the auth-requiring operators are a v2 roadmap, not shipped.

This is the +2 coding-agent bonus made concrete: a coding agent producing **reusable tooling for the
platform itself**, not just one submission.

## Build methodology (how a slice was driven)

1. `/speckit.plan` → `/speckit.analyze` → `/speckit.tasks` from the slice in
   `specs/003-uipath-native/tasks.md`.
2. **Spec Gate** per function — purpose / inputs / outputs / edge cases before any code.
3. **TDD** — offline structure test authored RED before the artifact (enforced by a pre-write
   hook for `agents/`, `shim/`, `mocks/`).
4. Author against the authoritative `uipath-*` skill; verify with the real `uip` CLI offline.
5. `/audit-ip-safety` (zero real-company tokens) + `uv run pytest` green before commit.
6. `/thermo-nuclear-code-quality-review` ↔ `/improve-codebase-architecture` on the slice diff.

## How the build maps to the 5 judging edges

- **Criterion 1 (real-world applicability):** a regulated-vertical crisis — payment-intermediary
  cyberattack with BAA/PHI boundaries and Trust-Layer guardrails — not a generic orchestration toy.
- **Criterion 2 (orchestration & agents):** 11 agents across 3 nested case levels; the Reversal-3
  6-way fan-out spawns 13 coordinated instances.
- **Criterion 3 (exceptions):** four-layer defense-in-depth, authored test-first (see README
  "Exception, Failure & Edge-Case Handling").
- **Criterion 4 (component variety):** 13 UiPath product surfaces / 37 artifacts (table above).
- **Criterion 5 (presentation):** live ≤5-min run + the Criterion-3 supplemental clip
  (`docs/submission/DEMO-criterion3-and-fanout.md`).
- **Coding-agent bonus (+2):** this document + `CLAUDE_CODE_USAGE.md` + `docs/coding-agents/` —
  Claude Code authored every artifact and every test, and the LangGraph coded agent is itself built
  *with* a coding agent end-to-end. It also went **beyond the project** to ship `Maestro Case Kit`
  (see "Above and beyond" above) — reusable open-source tooling for the platform itself. The +2
  coding-agent bonus (max score 27) rewards exactly this.

## IP safety

Every artifact and every line of evidence uses only the fictional cast (ClearFlow, Northstar,
Apex, Nimbus, Aurora Specialty, …). Zero real healthcare-company tokens — enforced by
`/audit-ip-safety` on each commit.
