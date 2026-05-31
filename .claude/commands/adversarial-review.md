---
description: Codex adversarial review (challenges design choices) via multi-model-router bridge
argument-hint: '[--background] [--base <ref>] [--scope auto|working-tree|branch] [focus text]'
---

Call `mcp__multi-model-router__codex_adversarial_review` for the current repo. Map `$ARGUMENTS`:
- `--background` → `background: true`
- `--base <ref>` → `base: "<ref>"`
- `--scope <s>` → `scope: "<s>"`
- Any free text after the flags → `focus: "<text>"`

Always set `repo_path` to the current repo's git root. Return Codex's output verbatim. This is review-only — do not apply any changes Codex suggests.
