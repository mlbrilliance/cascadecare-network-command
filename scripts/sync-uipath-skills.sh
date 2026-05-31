#!/usr/bin/env bash
# sync-uipath-skills.sh — Daily sync of UiPath skills from GitHub
# Checks for new/updated skills and agents, copies to all runtime directories,
# and flags changes for polyskill conversion.

set -euo pipefail

# --- Configuration ---
REPO_URL="https://github.com/uipath/skills.git"
PROJECT_DIR="/mnt/c/Users/linki/OneDrive/Desktop/cascade_command"
CACHE_DIR="$PROJECT_DIR/.cache/uipath-skills-upstream"
LOG_DIR="$PROJECT_DIR/scripts/logs"
PENDING_FILE="$PROJECT_DIR/.cache/pending-polyskill.json"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LOG_FILE="$LOG_DIR/sync-$(date +%Y%m%d-%H%M%S).log"

# Runtime target directories
CLAUDE_SKILLS="$PROJECT_DIR/.claude/skills"
CODEX_SKILLS="$PROJECT_DIR/.agents/skills"
COPILOT_SKILLS="$PROJECT_DIR/.github/skills"
CLAUDE_AGENTS="$PROJECT_DIR/.claude/agents"
CODEX_AGENTS="$PROJECT_DIR/.agents/agents"
COPILOT_AGENTS="$PROJECT_DIR/.github/agents"

# --- Setup ---
mkdir -p "$LOG_DIR" "$CACHE_DIR" "$(dirname "$PENDING_FILE")"

log() {
    echo "[$(date -u +"%H:%M:%S")] $*" | tee -a "$LOG_FILE"
}

log "=== UiPath Skills Sync Started ==="
log "Timestamp: $TIMESTAMP"

# --- Step 1: Clone or pull upstream repo ---
if [ -d "$CACHE_DIR/.git" ]; then
    log "Pulling latest from upstream..."
    cd "$CACHE_DIR"
    git fetch origin 2>>"$LOG_FILE"
    OLD_HEAD=$(git rev-parse HEAD)
    git reset --hard origin/main 2>>"$LOG_FILE" || git reset --hard origin/master 2>>"$LOG_FILE"
    NEW_HEAD=$(git rev-parse HEAD)

    if [ "$OLD_HEAD" = "$NEW_HEAD" ]; then
        log "No changes detected upstream. Nothing to do."
        log "=== Sync Complete (no changes) ==="
        exit 0
    fi
    log "Updated from $OLD_HEAD to $NEW_HEAD"
else
    log "Cloning upstream repository..."
    git clone --depth 1 "$REPO_URL" "$CACHE_DIR" 2>>"$LOG_FILE"
    cd "$CACHE_DIR"
    NEW_HEAD=$(git rev-parse HEAD)
    OLD_HEAD="initial"
    log "Initial clone complete at $NEW_HEAD"
fi

# --- Step 2: Detect skills and agents in upstream ---
UPSTREAM_SKILLS_DIR=""
if [ -d "$CACHE_DIR/skills" ]; then
    UPSTREAM_SKILLS_DIR="$CACHE_DIR/skills"
elif [ -d "$CACHE_DIR/.claude/skills" ]; then
    UPSTREAM_SKILLS_DIR="$CACHE_DIR/.claude/skills"
fi

UPSTREAM_AGENTS_DIR=""
if [ -d "$CACHE_DIR/agents" ]; then
    UPSTREAM_AGENTS_DIR="$CACHE_DIR/agents"
elif [ -d "$CACHE_DIR/.claude/agents" ]; then
    UPSTREAM_AGENTS_DIR="$CACHE_DIR/.claude/agents"
fi

if [ -z "$UPSTREAM_SKILLS_DIR" ]; then
    log "ERROR: Could not find skills directory in upstream repo"
    log "Checked: skills/, .claude/skills/"
    exit 1
fi

log "Skills source: $UPSTREAM_SKILLS_DIR"
log "Agents source: ${UPSTREAM_AGENTS_DIR:-none}"

# --- Step 3: Diff and identify changes ---
NEW_SKILLS=()
UPDATED_SKILLS=()
NEW_AGENTS=()
UPDATED_AGENTS=()

# Check skills
for skill_dir in "$UPSTREAM_SKILLS_DIR"/*/; do
    [ -d "$skill_dir" ] || continue
    skill_name=$(basename "$skill_dir")

    # Skip non-uipath skills (only sync uipath-* skills)
    if [[ "$skill_name" != uipath-* ]]; then
        continue
    fi

    if [ ! -d "$CLAUDE_SKILLS/$skill_name" ]; then
        NEW_SKILLS+=("$skill_name")
        log "NEW skill detected: $skill_name"
    else
        # Compare SKILL.md content
        upstream_md="$skill_dir/SKILL.md"
        local_md="$CLAUDE_SKILLS/$skill_name/SKILL.md"
        if [ -f "$upstream_md" ] && [ -f "$local_md" ]; then
            if ! diff -q "$upstream_md" "$local_md" >/dev/null 2>&1; then
                UPDATED_SKILLS+=("$skill_name")
                log "UPDATED skill detected: $skill_name"
            fi
        fi
    fi
done

# Check agents
if [ -n "$UPSTREAM_AGENTS_DIR" ]; then
    for agent_file in "$UPSTREAM_AGENTS_DIR"/*.md; do
        [ -f "$agent_file" ] || continue
        agent_name=$(basename "$agent_file")

        if [ ! -f "$CLAUDE_AGENTS/$agent_name" ]; then
            NEW_AGENTS+=("$agent_name")
            log "NEW agent detected: $agent_name"
        else
            if ! diff -q "$agent_file" "$CLAUDE_AGENTS/$agent_name" >/dev/null 2>&1; then
                UPDATED_AGENTS+=("$agent_name")
                log "UPDATED agent detected: $agent_name"
            fi
        fi
    done
fi

TOTAL_CHANGES=$(( ${#NEW_SKILLS[@]} + ${#UPDATED_SKILLS[@]} + ${#NEW_AGENTS[@]} + ${#UPDATED_AGENTS[@]} ))

if [ "$TOTAL_CHANGES" -eq 0 ] && [ "$OLD_HEAD" != "initial" ]; then
    log "Repo updated but no uipath-* skill/agent files changed."
    log "=== Sync Complete (no relevant changes) ==="
    exit 0
fi

log "Changes summary: ${#NEW_SKILLS[@]} new skills, ${#UPDATED_SKILLS[@]} updated skills, ${#NEW_AGENTS[@]} new agents, ${#UPDATED_AGENTS[@]} updated agents"

# --- Step 4: Copy to all runtime directories ---
copy_skill() {
    local skill_name="$1"
    local source_dir="$UPSTREAM_SKILLS_DIR/$skill_name"

    for target_dir in "$CLAUDE_SKILLS" "$CODEX_SKILLS" "$COPILOT_SKILLS"; do
        mkdir -p "$target_dir/$skill_name"
        cp -r "$source_dir"/* "$target_dir/$skill_name/"
    done
    log "  Copied $skill_name → claude, codex, copilot"
}

copy_agent() {
    local agent_file="$1"
    local source_path="$UPSTREAM_AGENTS_DIR/$agent_file"

    for target_dir in "$CLAUDE_AGENTS" "$CODEX_AGENTS" "$COPILOT_AGENTS"; do
        mkdir -p "$target_dir"
        cp "$source_path" "$target_dir/$agent_file"
    done
    log "  Copied agent $agent_file → claude, codex, copilot"
}

log "--- Installing new skills ---"
for skill in "${NEW_SKILLS[@]}"; do
    copy_skill "$skill"
done

log "--- Updating existing skills ---"
for skill in "${UPDATED_SKILLS[@]}"; do
    copy_skill "$skill"
done

log "--- Installing new agents ---"
for agent in "${NEW_AGENTS[@]}"; do
    copy_agent "$agent"
done

log "--- Updating existing agents ---"
for agent in "${UPDATED_AGENTS[@]}"; do
    copy_agent "$agent"
done

# --- Step 5: Update AGENTS.md if there are new skills ---
if [ ${#NEW_SKILLS[@]} -gt 0 ]; then
    log "--- Updating AGENTS.md with new skills ---"
    AGENTS_MD="$PROJECT_DIR/AGENTS.md"
    for skill in "${NEW_SKILLS[@]}"; do
        skill_md="$CLAUDE_SKILLS/$skill/SKILL.md"
        if [ -f "$skill_md" ]; then
            # Extract description from YAML frontmatter
            desc=$(sed -n '/^---$/,/^---$/p' "$skill_md" | grep -E "^description:" | sed 's/^description: *"\?//' | sed 's/"\?$//' | head -c 100)
            # Extract trigger from description
            trigger=$(echo "$desc" | grep -oP '`[^`]+`' | head -3 | tr '\n' ', ' | sed 's/, $//')
            [ -z "$trigger" ] && trigger="See SKILL.md"
            # Append to table (before the last line of the table section)
            echo "| **$skill** | $trigger | $desc |" >> "$AGENTS_MD"
            log "  Added $skill to AGENTS.md"
        fi
    done
fi

# --- Step 6: Write pending polyskill conversions ---
# This file signals to Claude Code that polyskill needs to run
ALL_CHANGED=("${NEW_SKILLS[@]}" "${UPDATED_SKILLS[@]}")

if [ ${#ALL_CHANGED[@]} -gt 0 ]; then
    # Build JSON array of changed skills
    json_skills=$(printf '"%s",' "${ALL_CHANGED[@]}")
    json_skills="[${json_skills%,}]"

    cat > "$PENDING_FILE" <<EOF
{
  "timestamp": "$TIMESTAMP",
  "commit": "$NEW_HEAD",
  "previous_commit": "$OLD_HEAD",
  "new_skills": $(printf '['; printf '"%s",' "${NEW_SKILLS[@]}" 2>/dev/null | sed 's/,$//'; printf ']'),
  "updated_skills": $(printf '['; printf '"%s",' "${UPDATED_SKILLS[@]}" 2>/dev/null | sed 's/,$//'; printf ']'),
  "new_agents": $(printf '['; printf '"%s",' "${NEW_AGENTS[@]}" 2>/dev/null | sed 's/,$//'; printf ']'),
  "updated_agents": $(printf '['; printf '"%s",' "${UPDATED_AGENTS[@]}" 2>/dev/null | sed 's/,$//'; printf ']'),
  "polyskill_targets": ["codex", "copilot", "cursor"],
  "status": "pending"
}
EOF
    log "Wrote pending polyskill conversions to $PENDING_FILE"
    log "Run '/polyskill all all' in Claude Code to convert changed skills"
fi

# --- Step 7: Cleanup old logs (keep last 30 days) ---
find "$LOG_DIR" -name "sync-*.log" -mtime +30 -delete 2>/dev/null || true

log ""
log "=== Sync Complete ==="
log "New skills: ${NEW_SKILLS[*]:-none}"
log "Updated skills: ${UPDATED_SKILLS[*]:-none}"
log "New agents: ${NEW_AGENTS[*]:-none}"
log "Updated agents: ${UPDATED_AGENTS[*]:-none}"
log ""
log "Next step: Open Claude Code and run '/polyskill all all' to convert for other runtimes"
