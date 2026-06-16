---
name: maestro-case-kit
description: >-
  Offline, credential-free knowledge + static validators for UiPath Maestro Case
  footguns. Explain cryptic error codes (400300, 160009, ...) and lint caseplans,
  spawn inputs, and Data Fabric specs in CI — no UiPath login. Use when authoring,
  debugging, or reviewing UiPath Maestro Case / Data Fabric / Action Center work.
license: MIT
metadata:
  homepage: https://github.com/mlbrilliance/cascadecare-network-command
  openclaw: true
allowed-tools:
  - Bash
---

# Maestro Case Kit

A living, version-stamped knowledge layer over undocumented UiPath **Maestro Case /
Data Fabric / Action Center** footguns, plus credential-free static validators. The
v1 surface needs **no UiPath login** — it runs offline and in CI. The same surface
is exposed three ways from one source: a `maestro-case` CLI, an MCP server
(`maestro-case-mcp`, stdio), and this skill.

## When to use

- An agent or developer hits a cryptic UiPath error code and search returns nothing.
- Before packing/deploying a Maestro Case, to catch inert-edit footguns in CI.
- Authoring Data Fabric entities, to avoid silent field-drops.

## Install

```bash
pipx install maestro-case-kit         # or: pip install maestro-case-kit
# MCP server (stdio) — register with your agent host:
#   command: maestro-case-mcp
```

## Commands (agent-native — every command takes --json and exits non-zero on findings)

- **Explain an error or footgun** (offline knowledge oracle):
  ```bash
  maestro-case explain 400300            # error code
  maestro-case explain underscore        # keyword
  maestro-case explain 160009 --json     # structured, for agents/CI
  ```
- **Lint a caseplan directory** (stale .bpmn, missing start event, dup output vars, bad V20 expressions):
  ```bash
  maestro-case lint path/to/caseplan-dir --json
  ```
- **Check spawn fan-out** (=datafabric.qem in spawn inputs → runtime 400300):
  ```bash
  maestro-case check-spawn path/to/caseplan-dir
  ```
- **Check a Data Fabric entity spec** (underscore silent-drop, reserved `id`):
  ```bash
  maestro-case check-df entity-spec.json
  ```

## Recipe — wire the validators into CI

Run the three validators in a pre-deploy job; non-zero exit fails the build before a
broken caseplan or a data-losing entity ships:

```bash
maestro-case lint "$CASEPLAN_DIR" \
  && maestro-case check-spawn "$CASEPLAN_DIR" \
  && maestro-case check-df "$ENTITY_SPEC"
```

## Recipe — explain a lint finding

Lint findings carry a rule id that maps to a knowledge entry; pass it to `explain`
for the full cause + fix:

```bash
maestro-case lint "$CASEPLAN_DIR" --json | jq -r '.[].entry_id' | sort -u \
  | xargs -I{} maestro-case explain {}
```

## Freshness

Every knowledge entry is stamped with the platform/CLI version it was proven on. When
UiPath fixes a footgun, the entry is marked `resolved_in` and drops from active
guidance — pass `--include-resolved` to `explain` to see history.

## MCP tools

The MCP server exposes the same surface as typed tools: `maestro_case_explain`,
`maestro_case_lint`, `maestro_case_check_spawn`, `maestro_case_check_df`.
