#!/usr/bin/env python3
"""AI security review — the skill-based layer. Runs on PRE-PUSH, not pre-commit.

Why pre-push and not pre-commit: this layer asks an AI agent to read the diff,
load the relevant cybersecurity skills, and reason about vulnerabilities. That is
slow (seconds to minutes) and costs tokens. Running it on every commit would make
committing painful. Pre-push is the right cadence — it runs once before code
leaves your machine, batching all the commits since the last push.

This script does NOT call an AI itself. It prepares a review brief — the diff plus
the routed skill domains — and writes it to a file, then prints instructions for
the agent to perform the review. In an agent-driven workflow (Claude Code, etc.)
the agent picks up the brief and runs the review using the cybersecurity skills.

Exit 0 always (it's advisory by default). Set REVIEW_BLOCKING=1 in the environment
to make a prepared-but-unreviewed push fail until the agent signs off.
"""
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROUTER = Path(__file__).parent / "skill_router.py"
BRIEF_DIR = Path(tempfile.gettempdir())


def get_push_range() -> str:
    """Commits being pushed: everything not yet on the remote tracking branch."""
    # Try to find the upstream; fall back to last 10 commits if none.
    r = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
        capture_output=True, text=True,
    )
    if r.returncode == 0 and r.stdout.strip():
        upstream = r.stdout.strip()
        return f"{upstream}..HEAD"
    return "HEAD~10..HEAD"


def main() -> None:
    diff_range = get_push_range()

    # Get the diff
    diff = subprocess.run(
        ["git", "diff", diff_range], capture_output=True, text=True
    ).stdout

    if not diff.strip():
        print("No changes to review.")
        sys.exit(0)

    # Run the router to find relevant skills
    routing = subprocess.run(
        [sys.executable, str(ROUTER), diff_range],
        capture_output=True, text=True,
    ).stdout

    if "No security-relevant changes" in routing:
        print("AI security review: no security-relevant changes detected. Skipping.")
        sys.exit(0)

    # Write the review brief
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    brief_path = BRIEF_DIR / f"security-review-brief-{ts}.md"
    brief = f"""# Security Review Brief
Generated: {datetime.now().isoformat()}
Diff range: {diff_range}

## Routed skill domains
{routing}

## Instructions for the reviewing agent
Load the skill domains listed above from the Anthropic-Cybersecurity-Skills repo.
For each changed hunk in the diff below, reason about whether it introduces a
vulnerability the loaded skills would flag. Produce findings as:

  SEVERITY (critical/high/medium/low) | file:line | issue | skill that applies | fix

If no issues, state "No security issues found" explicitly.

## Diff under review
```diff
{diff[:50000]}
```
{"" if len(diff) <= 50000 else "... (diff truncated at 50K chars; review remaining hunks separately)"}
"""
    brief_path.write_text(brief)

    print("=" * 60)
    print("AI SECURITY REVIEW REQUIRED BEFORE PUSH")
    print("=" * 60)
    print(routing)
    print(f"\nReview brief written to:\n  {brief_path}\n")
    print("Have your agent run the review:")
    print(f'  "Read {brief_path} and perform the security review it describes,')
    print('   loading the routed cybersecurity skills. Report findings."')
    print()

    if os.environ.get("REVIEW_BLOCKING") == "1":
        signoff = Path(str(brief_path) + ".signoff")
        if not signoff.exists():
            print("REVIEW_BLOCKING=1 and no signoff found. Push blocked.")
            print(f"After the agent reviews and you accept, create: {signoff}")
            sys.exit(1)

    # Advisory by default — don't block the push
    sys.exit(0)


if __name__ == "__main__":
    main()
