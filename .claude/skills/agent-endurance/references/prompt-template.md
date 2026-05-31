# Prompt Template for Long-Running Sessions

Adapt to your stack. Replace bracketed items.

---

```
Goal: Complete [MILESTONE_NAME] only: [brief description].

Verification: `make verify` — run after every meaningful edit. Do not skip.

Rules:
- Do not claim completion until `make verify` passes with zero failures.
- Never add:
  - Broad exception handlers (`except Exception`, empty `catch {}`)
  - `pass` in except/catch blocks
  - Mocked returns or stubbed functions in production code
  - Hardcoded success values or silent fallbacks
  - TODO/FIXME without a blocking test
- If a check fails, analyze the exact output and fix only that failure.
- If blocked 3+ consecutive attempts on the same issue, write a blocker note:
  what you tried, what failed, smallest possible next step.
- Only touch files relevant to this milestone.

Process:
1. Read all relevant files. Do not write code yet.
2. Plan (3-7 bullets): what changes and why.
3. Execute one subtask.
4. Run `make verify`.
5. Fix failures before next subtask.
6. Repeat 3-5 until complete.
7. Completion summary: changes, verify output, known limitations.

Milestones (do NOT work on future milestones):
- [M1]: [description] [CURRENT / done / blocked]
- [M2]: [description] [pending]
- [M3]: [description] [pending]
```

---

## Stack-specific verify targets

- **Python**: `pytest -x`, `ruff check .`, `mypy --strict src/`
- **TypeScript**: `npm test -- --runInBand`, `npx tsc --noEmit`, `npx eslint .`
- **Rust**: `cargo test`, `cargo clippy -- -D warnings`, `cargo fmt -- --check`
- **Go**: `go test ./...`, `go vet ./...`, `golangci-lint run`
- **C#/.NET**: `dotnet test`, `dotnet build --warnaserror`

Adjust the "never add" list per language (Rust: prohibit `unwrap()` in prod; Go: prohibit `_ = err`).
