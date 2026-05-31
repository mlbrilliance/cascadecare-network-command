# Claude Code Hooks Configuration

Place in `.claude/settings.json` at repo root.

## Python project

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "ruff format --quiet \"$CLAUDE_TOOL_INPUT_FILE_PATH\" 2>/dev/null; exit 0",
            "timeout": 10
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "make verify 2>&1 || { echo 'Verification failed.' >&2; exit 2; }",
            "timeout": 120
          }
        ]
      },
      {
        "hooks": [
          {
            "type": "command",
            "command": "scripts/check-no-fake-success.sh || exit 2",
            "timeout": 15
          }
        ]
      }
    ]
  }
}
```

## Node.js/TypeScript project

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write \"$CLAUDE_TOOL_INPUT_FILE_PATH\" --log-level silent 2>/dev/null; exit 0",
            "timeout": 10
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "npm test && npx tsc --noEmit && npx eslint . || { echo 'Checks failed.' >&2; exit 2; }",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

## How hooks work

- **PostToolUse**: Fires after tool completion. `matcher` is a regex against `tool_name`. Use for formatting.
- **Stop**: Fires when the agent tries to end its turn. Exit 2 with `blocking` semantics = agent cannot stop, must keep working.
- **PreToolUse**: Fires before tool execution. Exit 2 = block the tool call.
- **SessionStart**: Fires on session start. Stdout is injected as context.

The blocking Stop hook on `make verify` is the single most effective technique. The agent literally cannot claim "done" until all checks pass.

## Fake-success detection script

```bash
#!/bin/bash
# scripts/check-no-fake-success.sh
set -e

if grep -rn 'except Exception' --include='*.py' src/ 2>/dev/null; then
  echo "BLOCKED: Broad exception handler found" >&2
  exit 1
fi

if grep -Pn '^\s*pass\s*$' --include='*.py' -r src/ 2>/dev/null | grep -B1 'except'; then
  echo "BLOCKED: Empty except/pass block found" >&2
  exit 1
fi

echo "No fake-success patterns detected"
```
