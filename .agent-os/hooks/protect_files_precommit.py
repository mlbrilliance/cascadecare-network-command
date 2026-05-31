#!/usr/bin/env python3
"""Pre-commit adapter: block staged changes to protected files.

The Claude Code hook (protect_files.py) reads tool JSON from stdin. Pre-commit
instead passes the staged filenames as command-line arguments. This adapter
handles that calling convention so the same protected.txt governs both.
"""
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
    protected = load_protected()
    if not protected:
        sys.exit(0)

    staged = sys.argv[1:]
    violations = []
    for f in staged:
        name = Path(f).name
        for p in protected:
            if p in (f, name) or f.endswith(p):
                violations.append(f)
                break

    if violations:
        print("BLOCKED: commit modifies protected file(s):")
        for v in violations:
            print(f"  {v}")
        print("\nProtected files are immutable (see .agent-os/protected.txt).")
        print("Remove from protected.txt deliberately if this change is truly intended.")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
