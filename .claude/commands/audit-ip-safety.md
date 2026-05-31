---
description: "Scan entire repo for forbidden real-company names. Must pass before any commit."
user-invocable: true
---

# IP Safety Audit

Scan the entire repository for forbidden real-company tokens.

## Forbidden Tokens (case-insensitive)

- zelis
- aetna
- cigna
- unitedhealth
- unitedhealtcare
- bcbs
- blue cross
- blue shield
- hartley
- rivet
- zipp
- zapp
- change healthcare
- optum
- cotiviti
- wex

Also scan for patterns that suggest real data:
- Real claim number patterns (matching common EDI formats)
- Real NPI numbers (10-digit starting with specific prefixes)
- Real SSN patterns (XXX-XX-XXXX)

## Scan Scope

Scan ALL files in the repository EXCEPT:
- .git/
- .venv/
- node_modules/
- __pycache__/
- *.pyc
- knowledge/ (these are requirements docs, not build artifacts)
- .claude/skills/uipath-* (these are upstream UiPath skills, not our code)

## Steps

1. Use Grep to search for each forbidden token (case-insensitive) across the scan scope
2. Use Grep to search for suspicious data patterns
3. If ANY match is found:
   - Report FAIL with file path, line number, and matched token
   - List all violations
   - Exit with failure status
4. If NO matches found:
   - Report PASS: "IP safety audit passed. No forbidden tokens found."
   - Report scan statistics: files scanned, tokens checked

## Exit Codes

- PASS: No forbidden tokens found
- FAIL: One or more forbidden tokens found — do NOT commit
