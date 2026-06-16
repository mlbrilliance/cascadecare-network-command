# Contributing to Maestro Case Kit

The knowledge layer is the moat — it stays valuable only if entries are accurate,
version-stamped, and free of any real-world identifiers. Every contribution runs
through an automated **schema + IP-safety gate** before it can land.

## Add or update a knowledge entry

Entries live in [`src/maestro_case_kit/data/knowledge.json`](src/maestro_case_kit/data/knowledge.json).
Each entry has this shape:

| Field | Required | Notes |
|---|---|---|
| `id` | yes | Stable, unique, UPPER-KEBAB (e.g. `MC-SPAWN-QEM-400300`). |
| `kind` | yes | `runtime` / `data-fabric` / `hitl` / `cli` / `packaging` / `context-grounding` / ... |
| `title` | yes | One line. |
| `surface` | yes | Where it bites (e.g. `Maestro Case spawn JobArguments`). |
| `symptom` | yes | What the author observes. |
| `error_signatures` | list | Raw signatures `explain` matches on (`400300`, `still being indexed`); `[]` if silent. |
| `cause` | yes | Why it happens. |
| `fix` | yes | The proven workaround. |
| `proven_on` | yes | Platform/CLI version the behavior was confirmed on (e.g. `1.0.21`). |
| `resolved_in` | optional | Set when UiPath ships a fix — the entry then drops from active guidance. |
| `severity` | yes | `high` / `medium` / `low`. |
| `references` | list | Repo-relative paths or doc URLs. |

**Freshness is a feature.** Do not delete a fixed entry — set `resolved_in` so the
history survives and `explain --include-resolved` can still surface it.

**IP-safety is zero-tolerance.** No real company, product, patient, or claim names in
any field. Use generic or fictional placeholders.

## Run the gate locally

```bash
# Validate the bundled knowledge layer (schema + duplicate ids):
maestro-case validate-knowledge

# Validate a file against your own denylist (newline-delimited tokens, # comments ok):
maestro-case validate-knowledge --file path/to/knowledge.json --denylist-file denylist.txt
```

A non-zero exit means the gate found problems — fix them before opening a PR. Add a
test for any new validator rule or behavior; `pytest` must be green.
