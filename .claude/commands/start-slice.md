---
description: "Start work on a build slice. Verifies dependencies are done, sets status to in-progress, opens spec-kit feature."
user-invocable: true
---

# Start Slice

Begin work on slice `$ARGUMENTS` from the Master Build Roadmap.

## Steps

1. Read `tasks.md` at the project root
2. Find the slice matching the provided ID (e.g., "001", "002")
3. Verify all dependencies listed in "Depends on" have status `done`
   - If any dependency is not `done`, report which ones are blocking and stop
4. Set the slice's status to `in-progress` in tasks.md
5. Check if the spec-kit feature directory exists at `specs/{slice-id}-{slug}/`
   - If not, create it with a basic spec.md stub
6. If the spec-kit feature hasn't been specified yet (no detailed spec.md), suggest running `/speckit.specify` to generate the feature specification
7. Report: "Slice {id} — {name} is now in-progress. Dependencies verified. Ready to build."

## Validation

- Slice ID must exist in tasks.md
- All dependencies must be `done`
- No other slice should be `in-progress` for the same owner (warn if so)
