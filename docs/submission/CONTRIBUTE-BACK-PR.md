# Contribute-Back PR Plan — `UiPath/skills`

> **Status: DRAFT / PLAN — not an executed PR.** This document is the plan for a contribution
> back to [github.com/UiPath/skills](https://github.com/UiPath/skills). A **human** opens, pushes,
> and submits the PR; the coding agent does not. Nothing here has been pushed.
>
> **IP-safety:** this plan references only **UiPath** and our own fictional project names. No real
> company, patient, claim, or litigation identifiers appear anywhere (per `CLAUDE.md` forbidden-token
> list).

We built CascadeCare Network Command entirely on `UiPath/skills` and the `uip` CLI. While doing so
we hit three concrete defects in the published skills. We want to give the fixes back. This plan
groups them into **two PRs by difficulty**: a high-confidence namespace correction (#333 / #337) and
a lower-priority documentation/feature-gap report (#334).

---

## PR 1 — CLI namespace fix for the Maestro Case & Flow skills (#333, #337)

### The bug

The Maestro Case and Maestro Flow skills instruct the agent to call:

```
uip case ...        # in the Maestro Case skill (issue #333)
uip flow ...        # in the Maestro Flow skill (issue #337)
```

But the real CLI namespace is **nested under `maestro`**:

```
uip maestro case ...
uip maestro flow ...
```

An agent that follows the skill verbatim runs a command that does not exist, fails, and then has to
recover — exactly the kind of friction the skill is supposed to remove. We confirmed the correct
namespace empirically across five weeks of live use against Automation Cloud.

### The correction

- In the **Maestro Case** skill (issue **#333**): rewrite every `uip case <verb>` invocation to
  `uip maestro case <verb>` (authoring, instance, run, etc.).
- In the **Maestro Flow** skill (issue **#337**): rewrite every `uip flow <verb>` invocation to
  `uip maestro flow <verb>` (run, debug, eval, registry search, instances, etc.).
- Sweep prose, code fences, and any recipe blocks — not just the headline commands — so no stale
  `uip case` / `uip flow` form remains.

### Fallback if PR #399 is already merged at submission time

A fix may already be in flight upstream (**PR #399**). Before opening anything, **check whether #399
is merged.**

- **If #399 is NOT merged:** open this namespace-correction PR as described above and link #333 / #337.
- **If #399 IS merged:** do **not** re-fix the same lines. Pivot the contribution to **extending
  coverage** instead — e.g.:
  - add a short "common CLI footguns" note (the `uip maestro case` / `uip maestro flow` nesting, and
    that a `Completed` Case instance never flips its backing Orchestrator job to `Successful`);
  - add or extend a smoke test / doc-lint that asserts skill command snippets use the real namespace,
    so the regression cannot silently return.
  This keeps the contribution net-additive rather than a redundant re-fix.

### Priority

**High** — small, verifiable, high-confidence diff; directly improves every agent that uses these two
skills.

---

## PR 2 — `uipath-coded-apps` raw-curl workaround (#334)

### The report

The `uipath-coded-apps` skill currently instructs agents to **bypass the `uip` CLI and call the
platform with raw `curl`** for OAuth/token and deploy steps, because the corresponding `uip`
subcommands don't exist. That's a real gap: raw `curl` is brittle, leaks auth handling into agent
prose, and is easy to get wrong (we burned time on it ourselves).

### Why this is harder to "fix"

Unlike #333 / #337, this is **not** a one-line namespace correction — the underlying `uip`
subcommands genuinely don't exist yet, so the skill can't simply be pointed at a different command.
The right outcome is a **feature request to the CLI/skill owners** (add first-class OAuth + coded-app
deploy subcommands), with the skill updated once those land.

### The plan

- File / comment on **issue #334** as a **documentation + feature-gap report**, not a code PR.
- Include our concrete evidence: the working bare-deploy invocation we rely on
  (`uip codedapp deploy -n <name> --folder-key <key>`) and the gotcha that `-v` / `--path-name`
  **hangs forever** on "still being indexed". That at least lets the skill prefer the CLI path that
  *does* work and warn about the one that doesn't, even before new subcommands ship.
- Mark it clearly as lower priority than PR 1.

### Priority

**Low** — depends on upstream CLI feature work; the immediate value is documenting the working path
and the hang gotcha.

---

## Sequencing & ownership

1. **Human:** check upstream — is **PR #399** merged? Pick the PR 1 path (fix vs. extend-coverage)
   accordingly.
2. **Human:** open **PR 1** (namespace fix or coverage extension) referencing #333 / #337.
3. **Human:** comment on / file **#334** as a feature-gap report (PR 2), lower priority.
4. Run the upstream repo's own checks/tests before submitting each PR.

All authorship/diff drafting can be agent-assisted, but the **human reviews, opens, and pushes** every
PR. This file is the plan, not the PR.
