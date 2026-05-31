#!/usr/bin/env bash
# check-pending-polyskill.sh — Reports pending polyskill conversions from the
# daily UiPath skills sync. Run manually after sync-uipath-skills.sh, or wire a
# SessionStart hook in .claude/settings.json to invoke it automatically.
# (No such hook is configured by default — this script is opt-in.)

PENDING_FILE="/mnt/c/Users/linki/OneDrive/Desktop/cascade_command/.cache/pending-polyskill.json"

if [ -f "$PENDING_FILE" ]; then
    status=$(grep -o '"status": *"[^"]*"' "$PENDING_FILE" | head -1 | grep -o '"[^"]*"$' | tr -d '"')
    if [ "$status" = "pending" ]; then
        timestamp=$(grep -o '"timestamp": *"[^"]*"' "$PENDING_FILE" | head -1 | grep -o '"[^"]*"$' | tr -d '"')
        echo "⚡ UiPath skills were updated on $timestamp. Run '/polyskill all all' to convert for other runtimes."
        exit 0
    fi
fi
exit 0
