#!/usr/bin/env python3
"""PreToolUse hook: block bash commands that look like they leak or hardcode secrets.

Conservative — only blocks obvious patterns. Exits 2 to block in Claude Code.
"""
import json
import re
import sys

PATTERNS = [
    re.compile(r"(api[_-]?key|secret|password|token)\s*=\s*['\"][A-Za-z0-9_\-]{16,}['\"]", re.I),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),            # OpenAI-style keys
    re.compile(r"AKIA[0-9A-Z]{16}"),                # AWS access key
    re.compile(r"ghp_[A-Za-z0-9]{36}"),             # GitHub PAT
    re.compile(r"-----BEGIN (RSA |EC )?PRIVATE KEY-----"),
]


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    cmd = payload.get("tool_input", {}).get("command", "")
    if not cmd:
        sys.exit(0)

    for pat in PATTERNS:
        if pat.search(cmd):
            print("BLOCKED: command appears to contain a hardcoded secret.",
                  file=sys.stderr)
            print("Use an environment variable instead. Never put credentials in commands.",
                  file=sys.stderr)
            sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
