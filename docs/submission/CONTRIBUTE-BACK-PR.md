# Upstream Findings & the Anti-Regression Guard

> What we found in UiPath's *own* skills while building CascadeCare, the verified upstream status,
> and the concrete guard we shipped instead of a redundant PR.
> **IP-safety:** references only UiPath + our fictional project names — no real company/patient/claim
> identifiers (per `CLAUDE.md`).

## What we found

Building entirely on `UiPath/skills` and the `uip` CLI, we hit a concrete defect: the Maestro Case
and Maestro Flow skills instructed agents to call `uip case ...` / `uip flow ...`, but the real CLI
namespace is nested under `maestro` (`uip maestro case ...`, `uip maestro flow ...`). An agent that
follows the skill verbatim runs a command that does not exist, fails, and has to recover. (Issues
**#333**, **#337**; a third, **#334**, flagged the `uipath-coded-apps` skill steering agents to raw
`curl` for OAuth/deploy.)

## Current upstream status (verified 2026-06-16)

- **Already fixed on `main`.** Both `uipath-maestro-case` and `uipath-maestro-flow` now use the
  `uip maestro ...` namespace everywhere — **zero** bare `uip case` / `uip flow` remain.
- **PR #399** (the prior namespace fix) was **closed "due to age"** by a maintainer — not rejected;
  the correction landed independently via later skill rewrites.
- **#334** was resolved by **PR #401** (the raw-token guidance was removed).
- Issues **#333 / #337** remain *open* only as stale tracking metadata, not live defects.

**Conclusion:** a fresh namespace-fix PR would be an **empty diff** — there is nothing left to change.
We did **not** open one. (Opening a duplicate of a maintainer-closed PR against an already-fixed repo
would be noise, not a contribution.)

## What we shipped instead — a guard so it can't regress in *your* code

The namespace requirement is permanent — the `uip` CLI genuinely needs the `maestro` prefix — so the
trap stays live for anyone writing UiPath automation even though UiPath's skills are now correct.
Maestro Case Kit encodes it as durable knowledge **plus a static guard**:

- `maestro-case explain "unknown command"` → the `CLI-MAESTRO-NAMESPACE` entry (cause + fix).
- `maestro-case check-cli <path>` → flags bare `uip case` / `uip flow` / `uip bpmn` in your scripts
  and docs and points you at the `uip maestro ...` form. Credential-free; drops straight into CI.

So the real contribution is the **published, installable toolkit** (PyPI `maestro-case-kit`), which
turns a footgun we found in UiPath's own skills into a **reusable regression guard for the whole
community** — stronger and more durable than a redundant PR against an already-fixed repo.

## If you still want to engage upstream

The only remaining courtesy action is a comment on the stale-open **#333 / #337** noting they're
resolved on `main` (helps maintainers close them). That is outward-facing under your GitHub identity
— do it yourself; the agent will not post on your behalf.
