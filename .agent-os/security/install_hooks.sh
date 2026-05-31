#!/usr/bin/env bash
# Install the security hooks into git for this project.
# Run once from the repo root: bash .agent-os/security/install_hooks.sh
set -euo pipefail

echo "Installing agent-harness security hooks..."

# 1. pre-commit framework (handles the deterministic scan + protect + env checks)
if command -v pre-commit >/dev/null 2>&1; then
  echo "  pre-commit found — installing commit + push hooks"
  pre-commit install
  pre-commit install --hook-type pre-push
else
  echo "  pre-commit NOT found. Install it with: pip install pre-commit"
  echo "  Falling back to native git hooks for the deterministic scan."
  # Native fallback: write a pre-commit hook directly
  HOOK_DIR="$(git rev-parse --git-path hooks)"
  cat > "$HOOK_DIR/pre-commit" <<'HOOK'
#!/usr/bin/env bash
python3 .agent-os/hooks/security_scan.py || exit 1
python3 .agent-os/hooks/check_env_example.py || exit 1
# protected-file check needs the staged file list
staged=$(git diff --cached --name-only --diff-filter=ACM)
if [ -n "$staged" ]; then
  python3 .agent-os/hooks/protect_files_precommit.py $staged || exit 1
fi
HOOK
  chmod +x "$HOOK_DIR/pre-commit"
  echo "  Native pre-commit hook installed at $HOOK_DIR/pre-commit"
fi

# 2. pre-push AI review hook (native — always install, advisory by default)
HOOK_DIR="$(git rev-parse --git-path hooks)"
cp .agent-os/hooks/pre-push "$HOOK_DIR/pre-push"
chmod +x "$HOOK_DIR/pre-push"
echo "  pre-push AI security review hook installed at $HOOK_DIR/pre-push"

# 3. detect-secrets baseline (if available)
if command -v detect-secrets >/dev/null 2>&1; then
  if [ ! -f .secrets.baseline ]; then
    detect-secrets scan > .secrets.baseline
    echo "  detect-secrets baseline created"
  fi
fi

# 4. Check the cybersecurity skills are cloned
SKILLS_PATH=$(head -n1 .agent-os/security/config.txt 2>/dev/null | grep -v '^#' || echo "")
if [ -z "$SKILLS_PATH" ]; then
  SKILLS_PATH=$(grep -v '^#' .agent-os/security/config.txt 2>/dev/null | head -n1 || echo "")
fi
if [ -n "$SKILLS_PATH" ] && [ ! -d "$SKILLS_PATH" ]; then
  echo ""
  echo "  NOTE: cybersecurity skills not found at: $SKILLS_PATH"
  echo "  Clone them to enable the AI review layer:"
  echo "    git clone https://github.com/mukul975/Anthropic-Cybersecurity-Skills.git \\"
  echo "      ../Anthropic-Cybersecurity-Skills"
fi

echo ""
echo "Done. Two security layers are now active:"
echo "  - pre-commit: fast deterministic scan (blocks on secrets/dangerous patterns)"
echo "  - pre-push:   AI skill-based review (advisory; set REVIEW_BLOCKING=1 to enforce)"
