# CascadeCare Network Command — Developer Makefile
# All Python commands run via `uv run` so the virtual environment is always active.
# See .agent-os/project.md for full project configuration.

.PHONY: resume load-context init-db checkpoint save-session log-decision \
        test lint audit setup-mcps install-hooks help

# ── Memory system ─────────────────────────────────────────────────────────────

## resume         — print session context (run at START of every session)
resume:
	uv run python .agent-os/scripts/resume.py

## load-context   — alias for resume
load-context: resume

## init-db        — initialise the SQLite memory database (run once, or after DB loss)
init-db:
	uv run python .agent-os/scripts/init_db.py

## checkpoint     — record a subtask pass/fail result
##   make checkpoint TASK=S013 NAME=step-name PASSED=1 DETAILS="what happened"
checkpoint:
	uv run python .agent-os/scripts/checkpoint.py \
		--task_id "$(TASK)" \
		--checkpoint_name "$(NAME)" \
		--passed $(PASSED) \
		--details "$(DETAILS)"

## save-session   — save a session summary to memory (run at END of every session)
##   make save-session TASK=S013 SUMMARY="..." DECISIONS="..." BLOCKERS="none" NEXT="S014"
save-session:
	uv run python .agent-os/scripts/save_session.py \
		--summary "$(SUMMARY)" \
		--active_task "$(TASK)" \
		--decisions "$(DECISIONS)" \
		--blockers "$(BLOCKERS)" \
		--next_action "$(NEXT)"

## log-decision   — record a non-obvious architectural decision to the DB
##   make log-decision TASK=S013 DECISION="chose X" RATIONALE="because Y" ALT="considered Z"
log-decision:
	@uv run python -c "\
import sqlite3, datetime; \
conn = sqlite3.connect('.agent-os/memory/project_memory.db'); \
conn.execute('INSERT INTO decision_log (task_id, decision, rationale, alternatives_considered) VALUES (?,?,?,?)', \
             ('$(TASK)', '$(DECISION)', '$(RATIONALE)', '$(ALT)')); \
conn.commit(); conn.close(); \
print('Decision logged for task $(TASK).')"

# ── Development workflow ──────────────────────────────────────────────────────

## test           — run the full pytest suite
test:
	uv run pytest

## lint           — ruff lint + format + mypy type check
lint:
	uv run ruff check --fix
	uv run ruff format
	uv run mypy src/

## audit          — check for forbidden IP-safety tokens across the codebase
audit:
	@echo "=== IP Safety Audit ===" && \
	(grep -rniE \
		"zelis|aetna|cigna|unitedhealth|bcbs|hartley|rivet|zipp|zapp|change healthcare|optum|cotiviti|wex" \
		--include="*.py" --include="*.json" --include="*.md" \
		--include="*.yaml" --include="*.yml" --include="*.txt" \
		--exclude-dir=".git" --exclude-dir=".agent-os/memory" \
		--exclude-dir="node_modules" \
		. \
		&& echo "" && echo "FAIL: forbidden tokens found above." && exit 1) \
	|| echo "PASS: no forbidden tokens found."

# ── Setup ─────────────────────────────────────────────────────────────────────

## setup-mcps     — install the 4 project MCPs (requires .env with API keys filled in)
setup-mcps:
	bash scripts/setup-mcps.sh

## install-hooks  — install pre-commit + pre-push git hooks
install-hooks:
	bash .agent-os/security/install_hooks.sh

# ── Help ──────────────────────────────────────────────────────────────────────

## help           — show available targets
help:
	@echo "CascadeCare Network Command — Makefile targets:"
	@echo ""
	@grep -E '^## ' Makefile | sed 's/^## /  /'
