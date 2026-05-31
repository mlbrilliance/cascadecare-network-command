---
description: "Slice 016 — Coding-agent evidence consolidation implementation tasks"
---

# Tasks: Slice 016 — Coding-Agent Evidence Consolidation

**Input**: `specs/003-uipath-native/tasks.md` §Slice 016; `docs/changelog.md`; `agents/prompts/*.md`

**Goal**: Every UiPath artifact has at least one evidence channel proving a coding
agent (Claude Code) authored it; the AgentHack coding-agent bonus's (a) tool /
(b) contribution / (c) verifiable-evidence triad is documented and cross-linked.

## User Stories

- **US1** (P1): A Devpost judge can verify, from one canonical doc, that Claude Code
  authored every UiPath component and HOW — satisfying the 2-point coding-agent bonus.
- **US2** (P2): Each artifact type has a focused evidence page citing the real
  committed prompt templates + the build narrative.
- **US3** (P3): The prompt-log + screenshot channels are scaffolded with honest
  capture status (no fabricated transcripts/images).

## Evidence sources (durable, real)

- `docs/changelog.md` — 211-line per-slice build narrative.
- `agents/prompts/*.md` — 7 committed agent prompt templates (genuine artifacts).
- `specs/003-uipath-native/` — spec-kit authoring trail (plan/research/slice tasks).
- The 27 UiPath artifacts themselves (3 cases, 4 low-code agents, 3 coded agents,
  14 API workflows, 1 BPMN, 1 Flow, 1 App).

> git history is NOT an evidence source: it was collapsed to a clean-slate orphan
> commit during the Slice-015 secret purge. The changelog is the durable trail.

---

## Phase 1: Offline TDD gate

- [X] T001 [US1] Write `tests/unit/docs/test_coding_agents_evidence.py` — asserts
  `CODING_AGENTS.md` exists, names "Claude Code", carries the (a)/(b)/(c) bonus
  sections, and references every artifact group + the 27-artifact count; asserts
  each `docs/coding-agents/<type>.md` exists; IP-safe. RED first.

**Checkpoint**: gate exists and is RED.

---

## Phase 2: Channel 1 — canonical reference (OFFLINE)

- [X] T002 [US1] `CODING_AGENTS.md` (repo root) — canonical: tool = Claude Code;
  the full 27-artifact authorship table (artifact → type → slice → evidence
  pointer); build methodology (spec-kit, TDD, UiPath skills); the (a)/(b)/(c) triad.
- [X] T003 [US1] `CLAUDE_CODE_USAGE.md` (repo root) — concise Devpost-bonus doc
  (per CLAUDE.md), pointing at CODING_AGENTS.md for the full table.

---

## Phase 3: Channel 2 — per-artifact-type evidence (OFFLINE)

- [X] T004 [US2] `docs/coding-agents/{cases,agents-lowcode,agents-coded,api-workflows,bpmn,flow,apps}.md`
  — one cohesive page per artifact type (grouped over 27 fragmentary files to avoid
  shallow-doc sprawl), each naming its artifacts + the authoring agent + a real
  prompt/spec excerpt + changelog cross-link.
- [X] T005 [US2] `docs/coding-agents/README.md` — index + cross-links to all channels.

---

## Phase 4: Channels 3 & 4 — scaffold with honest capture status

- [X] T006 [US3] `docs/prompt-logs/README.md` — index citing `agents/prompts/*.md`
  as the committed prompt evidence + representative excerpts; marks live-session
  transcript capture as a human step (status: pending).
- [X] T007 [US3] `docs/coding-agents/screenshots/README.md` — capture checklist +
  pending status (images are a human capture step; not fabricated).

---

## Phase 5: Gate + commit

- [X] T008 GREEN: `uv run pytest tests/unit/docs/` passes; full suite green.
- [X] T009 IP-safety audit PASS on all new docs.
- [X] T010 Commit: `feat(slice-016): coding-agent evidence consolidated across 4 channels`

## Carried forward (human steps, not offline-completable)

- The 1-minute coding-agent reel (video) and live-session screenshots/transcripts
  are capture tasks for the submission session (Slice 017). Scaffolded + flagged here.
