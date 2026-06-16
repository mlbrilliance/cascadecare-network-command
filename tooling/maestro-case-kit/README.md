# Maestro Case Kit

[![PyPI](https://img.shields.io/pypi/v/maestro-case-kit.svg)](https://pypi.org/project/maestro-case-kit/)
[![Python](https://img.shields.io/pypi/pyversions/maestro-case-kit.svg)](https://pypi.org/project/maestro-case-kit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Offline, credential-free **knowledge + static validators** for UiPath **Maestro Case /
Data Fabric / Action Center** footguns. One define-once source, four artifacts: a Go-free
Python **CLI**, an **MCP server**, a Claude Code **skill**, and an OpenClaw **skill**.

> Built from behaviors discovered while running a multi-stakeholder crisis case end-to-end
> on UiPath Automation Cloud. The orchestration tier *above* the canvas is unserved by
> official tooling; this kit makes the hard-won knowledge installable and agent-native.

## Why

- UiPath's coding-agent MCP is a single catch-all `run_command` shell — not typed tools.
- Maestro Case error codes (`400300`, `160009`, `170015`, ...) return zero search results.
- Caseplan edits can be silently inert; Data Fabric fields can silently vanish on insert.

This kit encodes those footguns as a **version-stamped knowledge layer** + **CI linters**
that run with **no UiPath login**.

## Install

```bash
pipx install maestro-case-kit        # CLI: maestro-case ; MCP: maestro-case-mcp
```

## Use

```bash
maestro-case explain 400300                 # error code -> proven cause + fix (offline)
maestro-case lint   path/to/caseplan-dir    # static V20 lint (stale .bpmn, no start event, ...)
maestro-case check-spawn path/to/caseplan-dir   # =datafabric.qem in spawn inputs (400300)
maestro-case check-df  entity-spec.json     # Data Fabric underscore-drop / reserved id
```

Every command takes `--json` and exits non-zero when it has a finding, so it drops
straight into CI. See [`SKILL.md`](SKILL.md) for agent-host usage and recipes.

## MCP server

`maestro-case-mcp` speaks newline-delimited JSON-RPC over stdio (no third-party MCP SDK
dependency) and exposes typed tools: `maestro_case_explain`, `maestro_case_lint`,
`maestro_case_check_spawn`, `maestro_case_check_df`. Register it with any MCP host.

## One source, many harnesses

`SKILL.md` is the define-once skill source. Fan it out to other coding-agent runtimes
(Cursor, Codex, Gemini, Copilot, OpenClaw/ClawHub) with a skills converter — e.g.
`/polyskill` or `npx skills add`. The CLI and MCP server are generated from the same
shared tool registry (`maestro_case_kit/tools.py`), so a fix lands once and every surface
inherits it.

## Knowledge entries & contributions

Entries live in `maestro_case_kit/data/knowledge.json`, each stamped with the version it
was proven on and an optional `resolved_in`. Contributions run through an automated
IP-safety + schema gate (see `CONTRIBUTING.md`). License: MIT.
