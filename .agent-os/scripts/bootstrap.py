#!/usr/bin/env python3
"""Bootstrap the agent harness in a fresh project.

Run once after dropping the harness into an empty folder:
    python .agent-os/scripts/bootstrap.py

It initializes the memory DB, seeds protected.txt with the always-protected
files, creates an empty tasks.md, and prints the next steps. Idempotent.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
SCRIPTS = ROOT / ".agent-os" / "scripts"


def run(cmd: list[str]) -> None:
    print(f"  $ {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def main() -> None:
    print("Bootstrapping agent harness...\n")

    # 1. Init the memory DB
    print("1. Initializing memory database")
    run([sys.executable, str(SCRIPTS / "init_db.py")])

    # 2. Seed protected.txt if it has no real entries yet
    protected = ROOT / ".agent-os" / "protected.txt"
    content = protected.read_text() if protected.exists() else ""
    if "# ADD PROJECT-SPECIFIC" not in content:
        protected.write_text(
            "# Protected files — these are NEVER modified once created.\n"
            "# Agents will refuse to edit anything listed here.\n"
            "# One path per line, relative to repo root or bare filename.\n"
            "\n"
            ".agent-os/memory/project_memory.db\n"
            "\n"
            "# ADD PROJECT-SPECIFIC PROTECTED FILES BELOW\n"
            "# e.g. data/test_set.jsonl, config/production.yaml\n"
        )
        print("\n2. Seeded .agent-os/protected.txt")
    else:
        print("\n2. protected.txt already configured — skipped")

    # 3. Create empty tasks.md if absent
    tasks = ROOT / "tasks.md"
    if not tasks.exists():
        tasks.write_text(
            "# Tasks\n\n"
            "> Master task tracker. Generated from the approved plan during /plan.\n"
            "> Status values: [ ] not started, [~] in progress, [x] complete,\n"
            "> [!] blocked, [F] frozen.\n\n"
            "_No tasks yet. Run the planning workflow to populate this file._\n"
        )
        print("3. Created empty tasks.md")
    else:
        print("3. tasks.md already exists — skipped")

    # 4. Ensure .env.example exists
    env_example = ROOT / ".env.example"
    if not env_example.exists():
        env_example.write_text(
            "# Environment variables — copy to .env and fill in values.\n"
            "# .env is gitignored; this file (no values) is committed.\n"
            "# Add every variable your project needs here.\n"
        )
        print("4. Created .env.example")
    else:
        print("4. .env.example already exists — skipped")

    print("\n" + "=" * 60)
    print("BOOTSTRAP COMPLETE")
    print("=" * 60)
    print("""
Next steps:

1. Fill in the project description in AGENTS.md (the "What this project is"
   section) and CONTEXT.md (your domain vocabulary).

2. Add any always-protected files to .agent-os/protected.txt
   (e.g. a frozen test set, a production config).

3. Set your formatter/linter command in .agent-os/project.md.

4. Start the planning conversation with your agent. Tell it:
   "Read AGENTS.md and CONTEXT.md. Then let's plan this project.
    Grill me until you understand the scope, then produce a plan
    broken into tasks in tasks.md."

5. At the start of every future session, run:
   python .agent-os/scripts/resume.py
""")


if __name__ == "__main__":
    main()
