---
description: Convert one or more Agent Skills to other runtime formats (Codex, Copilot, Cursor, Windsurf, Antigravity, Gemini)
allowed-tools: Bash Read Write Edit Glob Grep
argument-hint: <target-format> [skill-names...] (e.g., "codex interview-me code-review-and-quality" or "copilot all")
---

You are the polyskill converter. The user wants to convert Agent Skills from Claude Code format into one or more target runtime formats.

## Your task

Parse the user's argument: `$ARGUMENTS`

The argument format is: `<target> [skill-name ...] [options]`

**Targets:** `codex`, `copilot`, `cursor`, `windsurf`, `antigravity`, `gemini`, `all`

**Skill names:** One or more skill directory names, or `all` to convert every skill in `.claude/skills/`.

**Examples:**
- `/polyskill codex interview-me` — convert interview-me to Codex format
- `/polyskill copilot all` — convert all skills to GitHub Copilot format
- `/polyskill cursor karpathy-guidelines code-review-and-quality` — convert two skills to Cursor format
- `/polyskill all all` — convert every skill to every target format

## Step 1: Resolve skills

If skills = `all`, scan `.claude/skills/*/SKILL.md` in the current project directory. List what was found.

If specific names given, verify each exists at `.claude/skills/<name>/SKILL.md`.

## Step 2: Resolve target(s)

If target = `all`, emit for: codex, copilot, cursor, windsurf, antigravity, gemini.

## Step 3: Convert

For each skill, read its `SKILL.md`, parse the YAML frontmatter (`name`, `description`, `allowed-tools`) and the markdown body. Then apply target-specific rules:

### → Codex

Output: `dist/codex/<skill-name>/SKILL.md` + `dist/codex/<skill-name>/agents/openai.yaml`

**SKILL.md frontmatter:**
```yaml
---
name: <name>
description: >-
  <front-loaded description starting with "Use when..." — max ~300 chars>
metadata:
  short-description: <one-line summary>
---
```

**Body changes:**
- Replace any `` !`command` `` with prose: "First, run `command` and review the output before continuing."
- Append a "Sandbox guidance" section listing each `allowed-tools` pattern with its reason.

**agents/openai.yaml:**
```yaml
interface:
  short_description: <short description>
  default_prompt: Use $<name> to ...
```

### → GitHub Copilot

Output: `dist/copilot/<skill-name>.instructions.md`

Format:
```markdown
---
applyTo: <glob pattern if scoped, or omit for universal>
---

<full skill body converted to flat markdown>
```

- Strip Claude-specific frontmatter entirely
- Filename IS the skill name
- Keep all process steps, red flags, verification checklists

### → Cursor

Output: `dist/cursor/<skill-name>.mdc`

Format:
```markdown
---
description: <skill description>
globs: <file globs if scoped, or omit>
alwaysApply: <true for universal skills, false for scoped>
---

<full skill body>
```

### → Windsurf

Output: `dist/windsurf/<skill-name>.md`

Format: Standard markdown with the skill body. No special frontmatter — Windsurf reads `.windsurfrules` or `.windsurf/rules/*.md`.

### → Antigravity

Output: `dist/antigravity/<skill-name>.md`

Format:
```markdown
---
name: <name>
description: <description>
triggers:
  - <trigger phrases>
---

<full skill body>
```

### → Gemini CLI

Output: `dist/gemini/<skill-name>.md`

Format: Standard markdown. Gemini reads from `.gemini/rules/` or `GEMINI.md`. Strip Claude-specific constructs, preserve behavioral content.

## Step 4: Report

After converting, show a summary:

```
Converted N skills → <target> format:

  skill-name-1 → dist/<target>/...
  skill-name-2 → dist/<target>/...

Total: N skills, M files written
```

If any conversions had lossy primitives, list the warnings.

## Important rules

- Create the `dist/` directory tree under the project root
- Do NOT modify the source skills — conversion is read-only on the source
- For batch operations, use parallel file writes where possible
- Show warnings for any primitives that don't translate cleanly
- If the user didn't specify arguments, ask which target and which skills
