#!/usr/bin/env python3
"""Route a git diff to the relevant cybersecurity skills.

The Anthropic-Cybersecurity-Skills repo has 754 skills across 26 domains. Loading
all of them costs ~22K tokens just for frontmatter and is wasteful — almost none
are relevant to a given diff. This script inspects what changed and emits the
handful of skill domains an AI reviewer should load.

Used by security_review.py (the pre-push AI layer) and can be run standalone to
see which skills would apply to the current staged changes.

Configure the skills location in .agent-os/security/config.txt (one line:
the path to the cloned skills repo, e.g. ../Anthropic-Cybersecurity-Skills/skills).
"""
import subprocess
import sys
from pathlib import Path

CONFIG = Path(__file__).parent.parent / "security" / "config.txt"

# Map file signals → cybersecurity skill domains worth loading.
# Keys are matched against file paths and extensions; values are domain dirs
# (and example skill names) in the cybersecurity skills repo.
ROUTES = {
    "api": {
        "match": ["/api/", "/routes/", "/endpoints/", "/controllers/",
                  "graphql", "fastapi", "express", "flask"],
        "domains": ["api-security", "web-application-security"],
        "examples": ["securing-rest-apis", "testing-graphql-security",
                     "preventing-owasp-api-top-10"],
    },
    "auth": {
        "match": ["auth", "login", "session", "jwt", "oauth", "password",
                  "credential", "token", "/iam/", "rbac", "permission"],
        "domains": ["identity-access-management", "cryptography"],
        "examples": ["hardening-authentication-flows",
                     "implementing-zero-trust-identity",
                     "secure-session-management"],
    },
    "infra": {
        "match": [".tf", ".tfvars", "terraform", "cloudformation", "/k8s/",
                  "kubernetes", "helm", "dockerfile", "docker-compose",
                  ".github/workflows/", "/ci/", "/cd/"],
        "domains": ["devsecops", "container-security", "cloud-security"],
        "examples": ["auditing-terraform-configurations",
                     "securing-ci-cd-pipelines",
                     "scanning-container-images"],
    },
    "cloud": {
        "match": ["aws", "azure", "gcp", "boto3", "s3", "lambda", "iam-policy"],
        "domains": ["cloud-security"],
        "examples": ["hardening-aws-iam-policies",
                     "detecting-cloud-misconfigurations"],
    },
    "data": {
        "match": ["sql", "query", "database", "orm", "/db/", "migration",
                  "psycopg", "sqlalchemy", "prisma"],
        "domains": ["web-application-security"],
        "examples": ["preventing-sql-injection",
                     "securing-database-access"],
    },
    "crypto": {
        "match": ["encrypt", "decrypt", "cipher", "hash", "tls", "ssl",
                  "certificate", "/crypto/", "hmac", "rsa", "aes"],
        "domains": ["cryptography"],
        "examples": ["implementing-tls-correctly",
                     "secure-key-management"],
    },
    "deps": {
        "match": ["requirements.txt", "package.json", "pyproject.toml",
                  "go.mod", "cargo.toml", "gemfile", "pom.xml", "yarn.lock",
                  "package-lock.json"],
        "domains": ["vulnerability-management", "devsecops"],
        "examples": ["auditing-dependency-vulnerabilities",
                     "prioritizing-cve-remediation"],
    },
    "secrets_handling": {
        "match": [".env", "config", "settings", "vault", "secret"],
        "domains": ["devsecops", "compliance-governance"],
        "examples": ["managing-secrets-securely",
                     "auditing-secret-storage"],
    },
}


def get_skills_path() -> Path | None:
    if not CONFIG.exists():
        return None
    line = CONFIG.read_text().strip().splitlines()
    if not line:
        return None
    p = Path(line[0].strip())
    if not p.is_absolute():
        p = (CONFIG.parent.parent.parent / p).resolve()
    return p if p.exists() else None


def changed_files(diff_range: str | None) -> list[str]:
    if diff_range:
        cmd = ["git", "diff", "--name-only", diff_range]
    else:
        cmd = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"]
    out = subprocess.run(cmd, capture_output=True, text=True)
    return [l.strip().lower() for l in out.stdout.splitlines() if l.strip()]


def _matches(signal: str, filepath: str) -> bool:
    """Match a routing signal against a file path.

    Signals wrapped in slashes (e.g. '/api/') match a path segment anywhere,
    including a leading top-level directory ('api/users.py'). Other signals
    (extensions, substrings like 'jwt') match anywhere in the path.
    """
    if signal.startswith("/") and signal.endswith("/"):
        seg = signal.strip("/")
        # match as a path segment: start of path, or between slashes
        parts = filepath.split("/")
        return seg in parts
    return signal in filepath


def route(files: list[str]) -> dict:
    hits: dict = {}
    for category, spec in ROUTES.items():
        for f in files:
            if any(_matches(m, f) for m in spec["match"]):
                hits[category] = spec
                break
    return hits


def main() -> None:
    diff_range = sys.argv[1] if len(sys.argv) > 1 else None
    files = changed_files(diff_range)
    if not files:
        print("No changed files to route.")
        return

    hits = route(files)
    if not hits:
        print("No security-relevant changes detected by the router.")
        print("(General code review still applies; no specific security domain matched.)")
        return

    skills_path = get_skills_path()
    print("Security-relevant changes detected. Recommended skill domains to load:\n")
    for category, spec in hits.items():
        print(f"  [{category}]")
        for d in spec["domains"]:
            loc = f"{skills_path}/{d}/" if skills_path else f"<skills>/{d}/"
            print(f"    domain: {loc}")
        for ex in spec["examples"]:
            print(f"    e.g.    {ex}")
        print()

    if not skills_path:
        print("NOTE: skills repo path not configured. Set it in")
        print("      .agent-os/security/config.txt to enable AI review.")


if __name__ == "__main__":
    main()
