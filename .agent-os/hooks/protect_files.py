#!/usr/bin/env python3
"""PreToolUse hook: block edits to protected files.

Reads the file path the agent is trying to write from stdin (Claude Code passes
tool input as JSON on stdin). Exits 2 to block if the path is protected.

Works as a Claude Code hook. For other agents, the same rule is enforced by
instruction via AGENTS.md.
"""
import json
import sys
from pathlib import Path

PROTECTED_LIST = Path(__file__).parent.parent / "protected.txt"


def load_protected() -> set[str]:
    if not PROTECTED_LIST.exists():
        return set()
    return {
        line.strip()
        for line in PROTECTED_LIST.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    }


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # can't parse — don't block

    # Claude Code passes tool_input with file_path for Edit/Write tools
    tool_input = payload.get("tool_input", {})
    target = tool_input.get("file_path") or tool_input.get("path", "")
    if not target:
        sys.exit(0)

    protected = load_protected()
    target_name = Path(target).name
    target_rel = target

    for p in protected:
        if p in (target_rel, target_name) or target_rel.endswith(p):
            print(f"BLOCKED: {target} is a protected file (see .agent-os/protected.txt).",
                  file=sys.stderr)
            print("Protected files are immutable. If this change is truly needed,",
                  file=sys.stderr)
            print("remove the file from protected.txt deliberately and explain why.",
                  file=sys.stderr)
            sys.exit(2)  # exit 2 blocks the tool call in Claude Code

    sys.exit(0)


if __name__ == "__main__":
    main()
