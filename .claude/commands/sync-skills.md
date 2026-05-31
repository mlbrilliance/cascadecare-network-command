---
description: Sync UiPath skills from upstream GitHub repo, install new/updated skills, and run polyskill conversion
allowed-tools: Bash Read Write Edit Glob Grep
---

You are the UiPath skills sync coordinator. Run the daily sync manually and handle polyskill conversion.

## Task

1. Run the sync script to check for upstream changes:

```bash
bash /mnt/c/Users/linki/OneDrive/Desktop/cascade_command/scripts/sync-uipath-skills.sh
```

2. Check the output. If new or updated skills were found:
   - Read `.cache/pending-polyskill.json` to see what changed
   - Run `/polyskill all all` to convert the changed skills for all runtimes
   - After conversion completes, mark the sync as done:
     ```bash
     bash /mnt/c/Users/linki/OneDrive/Desktop/cascade_command/scripts/mark-polyskill-done.sh
     ```

3. If no changes were found, report that skills are up to date.

## Report Format

After completing, show:
```
Skills Sync Report
─────────────────
Status: [up-to-date | N new, M updated]
New skills: [list or "none"]
Updated skills: [list or "none"]
Polyskill conversion: [completed | not needed]
Last sync: [timestamp]
```
