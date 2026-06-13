# Claude Code Usage — AgentHack 2026 Coding-Agent Bonus

This project was built end-to-end with **Claude Code** (Anthropic's official CLI). This page is
the concise bonus-submission summary; the full 27-artifact authorship table and methodology are
in [`CODING_AGENTS.md`](CODING_AGENTS.md).

**(a) Which coding agent.** Claude Code (Claude Opus / Sonnet), driving the UiPath `uip` CLI and
the official `uipath-*` authoring skills.

**(b) How it contributed.** Claude Code authored 100% of the runtime artifacts — 3 Maestro Case
definitions, 4 Agent Builder agents, 3 Coded Agents, 14 API Workflows, 1 BPMN model, 1 Maestro
Flow, 1 UiPath App — plus the solution packaging, Data Fabric seeding, and 470+ offline test
gates. It worked in test-gated slices under a spec-kit workflow (`/speckit.plan → analyze →
tasks → implement`), Spec-Gate-per-function, TDD (tests before source), and a zero-tolerance
IP-safety audit on every commit. Diagnoses were empirical: e.g. Orchestrator **Error 2005** was
root-caused by packing an Api project offline and comparing the generated `package-descriptor.json`
to the nupkg contents — then fixed and re-proved offline.

**(c) Verifiable evidence.**
- [`CODING_AGENTS.md`](CODING_AGENTS.md) — canonical authorship table.
- [`docs/coding-agents/`](docs/coding-agents/) — per-type evidence pages.
- [`docs/changelog.md`](docs/changelog.md) — durable per-slice build narrative.
- [`agents/prompts/*.md`](agents/prompts/) — 7 committed agent prompt templates.
- [`specs/003-uipath-native/`](specs/003-uipath-native/) — the spec-kit authoring trail.
- [`tests/`](tests/) — the offline gates Claude Code wrote before each artifact.
- [`apps/clearflow-network-command/web/`](apps/clearflow-network-command/web/) — the live Coded
  Web App (React + Vite + UiPath TS SDK), authored and iteratively redesigned by Claude Code from
  a plain page to a mission-control center to the final **Energy-Flow** design (charcoal/orange,
  sidebar shell, cable cascade). Verifiable in git history — commits `fa702f1` (mission-control),
  `de55974` (constellation), `4a3dd07` (Energy-Flow), each pack/publish/deployed live via `uip
  codedapp`. The redesign slice ran the mandatory `/thermo-nuclear-code-quality-review` +
  `/improve-codebase-architecture` loop, applying every Blocker before commit.
