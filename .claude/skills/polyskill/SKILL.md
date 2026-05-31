---
name: polyskill
description: >
  Cross-runtime skill converter and optimizer. Use when the user wants to convert one or more Agent Skills into formats for other runtimes: OpenAI Codex, GitHub Copilot, Cursor, Windsurf, Antigravity, Gemini CLI, or any future runtime. Also use when importing an existing skill from another runtime, building cross-runtime versions, or troubleshooting why a skill behaves differently across runtimes.
allowed-tools: Bash Read Write Edit Glob Grep
---

# polyskill — Cross-Runtime Skill Converter

You are the **polyskill** converter. You take Agent Skills written for one runtime and emit optimized versions for any target runtime the user requests.

## When this skill should run

Activate when the user asks any of:

- "Convert my skill to codex / copilot / cursor / windsurf / antigravity / gemini format"
- "Package my skill for Codex" / "Package my skill for Copilot"
- "Make this skill work in both Claude Code and Codex"
- "Export all my skills to Codex format"
- "Import this Codex skill into Claude Code"
- "Build a cross-runtime version of `<skill>`"

## Supported target runtimes

| Target | Output format | Install location |
|--------|--------------|-----------------|
| **claude** | `SKILL.md` with YAML frontmatter (`name`, `description`, `allowed-tools`) | `~/.claude/skills/<name>/SKILL.md` |
| **codex** | `SKILL.md` (front-loaded description, sandbox guidance) + `agents/openai.yaml` sidecar | `~/.agents/skills/<name>/` |
| **copilot** | `.github/copilot-instructions.md` or `.github/instructions/<name>.instructions.md` | `.github/instructions/` in repo |
| **cursor** | `.cursor/rules/<name>.mdc` with Cursor rule format | `.cursor/rules/` in repo |
| **windsurf** | `.windsurfrules` or `.windsurf/rules/<name>.md` | `.windsurf/rules/` in repo |
| **antigravity** | `.antigravity/skills/<name>.md` | `.antigravity/skills/` in repo |
| **gemini** | `.gemini/rules/<name>.md` or `GEMINI.md` | `.gemini/rules/` in repo |

## Conversion rules per target

### Claude Code → Codex

1. **Front-load the description.** Codex has an ~8K char catalog cap across all skills. Move the "Use when..." triggers into the first line of the description.
2. **Rewrite dynamic injections.** Claude's `` !`command` `` syntax doesn't exist in Codex. Replace with prose: "First, run `command` and review the output before continuing."
3. **Emit `agents/openai.yaml` sidecar.** Contains `interface.short_description` and any `dependencies.tools` (MCP servers).
4. **Surface `allowed-tools` as sandbox guidance.** Append a "Sandbox guidance" section listing bash patterns the skill needs.
5. **Strip Claude-specific frontmatter.** Remove `allowed-tools`, `model`, `argument-hint` — Codex doesn't read these.

### Claude Code → GitHub Copilot

1. **Convert to `.instructions.md` format.** Copilot uses fenced instruction files with optional YAML frontmatter containing `applyTo` globs.
2. **Flatten structure.** Copilot instructions are flat markdown — no YAML `name`/`description` frontmatter. The filename IS the name.
3. **Preserve behavioral content.** The process steps, red flags, verification checklists all transfer directly.
4. **Add `applyTo` if the skill is file-type scoped.** E.g., a frontend skill gets `applyTo: "**/*.tsx,**/*.jsx"`.

### Claude Code → Cursor

1. **Convert to `.mdc` format.** Cursor uses MDC (Markdown Components) with frontmatter: `description`, `globs`, `alwaysApply`.
2. **Set `alwaysApply: true`** for universal skills (karpathy-guidelines, code-review-and-quality). Set `alwaysApply: false` + appropriate `globs` for scoped skills.
3. **Body is standard markdown.** Transfer the skill body directly.

### Claude Code → Windsurf

1. **Convert to Windsurf rules format.** Similar to Cursor — markdown with optional metadata.
2. **Place in `.windsurf/rules/` or as `.windsurfrules`** at repo root for global rules.

### Claude Code → Antigravity

1. **Convert to Antigravity skill format.** Markdown with YAML frontmatter containing `name`, `description`, `triggers`.
2. **Preserve the full body** — Antigravity skills are structurally similar to Claude Code skills.

### Claude Code → Gemini CLI

1. **Convert to Gemini rules format.** Markdown placed in `.gemini/rules/` or appended to `GEMINI.md`.
2. **Strip Claude-specific constructs.** Remove `allowed-tools`, dynamic injections.
3. **Preserve behavioral content** directly.

## The conversion process

### Step 1: Identify source skills

If the user names specific skills, locate them. If they say "all my skills" or "everything," scan:
- `<project>/.claude/skills/*/SKILL.md` — project-level skills
- `~/.claude/skills/*/SKILL.md` — global skills

List what was found and confirm with the user before converting.

### Step 2: Identify target format(s)

Ask which target(s) if not specified. Multiple targets can be emitted in one pass.

### Step 3: Convert each skill

For each skill × target combination:

1. Read the source SKILL.md
2. Parse YAML frontmatter (name, description, allowed-tools, etc.)
3. Parse markdown body (sections, code blocks, tables, checklists)
4. Apply the target-specific conversion rules above
5. Write the output file(s) to `dist/<target>/<skill-name>/` in the project

### Step 4: Optionally install

If the user says "install" or "activate," copy from `dist/` to the target's well-known directory. Confirm before overwriting existing files.

## Batch conversion

When converting multiple skills, show progress:

```
Converting 23 skills → codex format:
  [1/23] using-agent-skills .......... OK
  [2/23] interview-me ................ OK
  ...
  [23/23] shipping-and-launch ........ OK

Output: dist/codex/ (23 skills, 46 files)
```

## What polyskill will NOT do

- It will not invent skill content. It converts existing content between formats.
- It will not auto-publish to marketplaces.
- It will not modify runtime configuration files (settings.json, config.toml, etc.).

## Handling lossy conversions

Some primitives don't translate cleanly. Always warn the user:

| Primitive | Claude Code | Codex | Copilot | Cursor |
|-----------|------------|-------|---------|--------|
| Dynamic injection (`` !`cmd` ``) | Native | Rewrite as prose | Not supported | Not supported |
| `allowed-tools` frontmatter | Honored | Ignored (→ sandbox section) | Not applicable | Not applicable |
| `agents/openai.yaml` sidecar | Not read | Required for UI | Not applicable | Not applicable |
| `alwaysApply` / `globs` scoping | Not applicable | Not applicable | `applyTo` globs | Native `.mdc` |
| MCP dependencies | In body or config | In `openai.yaml` | Not applicable | Not applicable |

When a primitive is lost, emit a `<!-- POLYSKILL WARNING: ... -->` comment in the output so future reads know what was dropped.

## Source

Polyskill is based on the open Agent Skills standard. Reference: https://github.com/earlyaidopters/polyskill
