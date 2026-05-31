#!/usr/bin/env bash
# mark-polyskill-done.sh — Mark pending polyskill conversions as completed
# Run after /polyskill finishes converting skills.

PENDING_FILE="/mnt/c/Users/linki/OneDrive/Desktop/cascade_command/.cache/pending-polyskill.json"

if [ -f "$PENDING_FILE" ]; then
    sed -i 's/"status": "pending"/"status": "completed"/' "$PENDING_FILE"
    echo "Marked polyskill conversions as completed."
fi
