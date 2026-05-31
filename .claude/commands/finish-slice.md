---
description: "Finish a build slice. Runs acceptance tests, marks done, logs changelog, commits."
user-invocable: true
---

# Finish Slice

Complete work on slice `$ARGUMENTS` from the Master Build Roadmap.

## Steps

1. Read `tasks.md` at the project root
2. Find the slice matching the provided ID
3. Verify the slice status is `in-progress`
4. Run the slice's acceptance tests:
   - `uv run pytest tests/ -k "slice_{id}" -v` (if slice-specific tests exist)
   - `uv run pytest` (full test suite must also pass)
5. Run linting: `uv run ruff check .`
6. Run type checking: `uv run mypy src/`
7. Run IP safety audit: grep for forbidden tokens
8. If all checks pass:
   - Set slice status to `done` in tasks.md
   - Add a one-paragraph completion summary to docs/changelog.md (create if doesn't exist)
   - Stage changes and commit with message: `slice-{id}: {name} complete`
9. If any check fails:
   - Report which checks failed
   - Do NOT mark as done
   - Suggest fixes

## Validation

- Slice must exist and be `in-progress`
- All tests must pass
- Linter must pass
- IP safety must pass
