#!/usr/bin/env python3
"""Deterministic security scan — runs on every commit via pre-commit.

This is the FAST, BLOCKING layer. No AI, no network, no tokens. It catches the
high-frequency mistakes (secrets, obvious dangerous patterns) in milliseconds so
they never reach the repo. The AI skill-based review (security_review.py) is a
separate, slower layer that runs on pre-push instead.

Exit 0 = clean, commit proceeds.
Exit 1 = findings, commit blocked.
"""
import re
import subprocess
import sys
from pathlib import Path

# ---- Secret patterns (high-confidence only — avoid false positives) ----
SECRET_PATTERNS = [
    ("OpenAI key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("AWS secret key", re.compile(r"aws_secret_access_key\s*=\s*['\"][A-Za-z0-9/+]{40}['\"]", re.I)),
    ("GitHub PAT", re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}")),
    ("Slack token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("Google API key", re.compile(r"AIza[0-9A-Za-z_\-]{35}")),
    ("Private key block", re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("Generic assigned secret", re.compile(
        r"(?:api[_-]?key|secret|passwd|password|token|bearer)\s*[:=]\s*['\"][^'\"]{12,}['\"]", re.I)),
    ("JWT", re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
]

# ---- Dangerous code patterns (language-agnostic high-signal) ----
DANGER_PATTERNS = [
    ("eval on dynamic input", re.compile(r"\beval\s*\(")),
    ("exec on dynamic input", re.compile(r"\bexec\s*\(")),
    ("shell=True with f-string", re.compile(r"shell\s*=\s*True")),
    ("pickle.loads (deser RCE)", re.compile(r"pickle\.loads?\s*\(")),
    ("yaml.load without SafeLoader", re.compile(r"yaml\.load\s*\((?!.*SafeLoader)")),
    ("hardcoded 0.0.0.0 bind", re.compile(r"['\"]0\.0\.0\.0['\"]")),
    ("disabled TLS verify", re.compile(r"verify\s*=\s*False")),
    ("subprocess with shell string", re.compile(r"os\.system\s*\(")),
]

# File extensions worth scanning for code patterns
CODE_EXTS = {".py", ".js", ".ts", ".jsx", ".tsx", ".rb", ".go", ".java", ".php",
             ".sh", ".bash", ".yaml", ".yml", ".tf", ".sql", ".c", ".cpp", ".cs"}

# Never scan these (binary, vendored, generated)
SKIP_DIRS = {"node_modules", ".git", "dist", "build", "target", ".venv", "venv",
             "__pycache__", "vendor", ".agent-os"}


def staged_files() -> list[Path]:
    """Files staged for this commit (added/copied/modified)."""
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True, text=True,
    )
    files = []
    for line in out.stdout.splitlines():
        p = Path(line.strip())
        if not p.exists():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        files.append(p)
    return files


def scan_file(path: Path) -> list[tuple[int, str, str]]:
    findings = []
    try:
        text = path.read_text(errors="ignore")
    except Exception:
        return findings
    lines = text.splitlines()
    for i, line in enumerate(lines, 1):
        # secret patterns apply to all text files
        for label, pat in SECRET_PATTERNS:
            if pat.search(line):
                findings.append((i, "SECRET", f"{label}"))
        # code patterns only for code files
        if path.suffix in CODE_EXTS:
            for label, pat in DANGER_PATTERNS:
                if pat.search(line):
                    findings.append((i, "DANGER", f"{label}"))
    return findings


def main() -> None:
    files = staged_files()
    if not files:
        sys.exit(0)

    total = 0
    print("Security scan (deterministic, pre-commit)...")
    for f in files:
        findings = scan_file(f)
        if findings:
            for line_no, kind, label in findings:
                print(f"  [{kind}] {f}:{line_no} — {label}")
                total += 1

    if total:
        print(f"\n{total} security finding(s). Commit blocked.")
        print("Fix the findings, or if a match is a false positive, refactor to")
        print("avoid the pattern (move secrets to env vars, avoid eval/exec, etc.).")
        print("To bypass in a genuine emergency: git commit --no-verify (discouraged).")
        sys.exit(1)

    print("  clean.")
    sys.exit(0)


if __name__ == "__main__":
    main()
