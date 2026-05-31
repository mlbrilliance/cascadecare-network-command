#!/usr/bin/env python3
"""Pre-commit hook: ensure .env.example stays in sync with .env.

If .env exists and defines a variable not present in .env.example, block the
commit. This stops the common drift where someone adds a config var to .env but
forgets to document it in the committed example file.
"""
import sys
from pathlib import Path


def keys(path: Path) -> set[str]:
    if not path.exists():
        return set()
    out = set()
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            out.add(line.split("=", 1)[0].strip())
    return out


def main() -> None:
    env = Path(".env")
    example = Path(".env.example")
    if not env.exists():
        sys.exit(0)  # nothing to check
    missing = keys(env) - keys(example)
    if missing:
        print("BLOCKED: .env.example is missing keys present in .env:")
        for k in sorted(missing):
            print(f"  {k}")
        print("\nAdd them to .env.example (with empty values) before committing.")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
