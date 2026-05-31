#!/usr/bin/env bash
# Install 4 project-scoped MCPs from .env API keys.
# Usage: bash scripts/setup-mcps.sh
#
# Run this ONCE after filling in your API keys in .env.
# Safe to re-run — removes stale entries before re-adding.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ ! -f .env ]; then
  echo "Error: .env not found."
  echo "  cp .env.example .env"
  echo "  # fill in CONTEXT7_API_KEY, REF_API_KEY, REF_MCP_URL, EXA_API_KEY, TAVILY_API_KEY"
  exit 1
fi

# Export vars from .env (ignore comments and blanks).
# Parsed line-by-line so values with parens/brackets don't cause eval errors.
while IFS= read -r line || [[ -n "$line" ]]; do
  # Skip comments and blank lines
  [[ "$line" =~ ^[[:space:]]*# ]] && continue
  [[ -z "${line// }" ]] && continue
  # Split on first '=' only
  key="${line%%=*}"
  value="${line#*=}"
  # Strip surrounding single or double quotes from value
  value="${value#\"}" ; value="${value%\"}"
  value="${value#\'}" ; value="${value%\'}"
  [[ -n "$key" ]] && export "$key"="$value"
done < .env

# Validate required vars
MISSING=()
for var in CONTEXT7_API_KEY REF_API_KEY REF_MCP_URL EXA_API_KEY TAVILY_API_KEY; do
  val="${!var:-}"
  if [ -z "$val" ]; then
    MISSING+=("$var")
  fi
done
if [ ${#MISSING[@]} -gt 0 ]; then
  echo "Error: missing values in .env:"
  for v in "${MISSING[@]}"; do echo "  $v=<not set>"; done
  echo "Fill them in and re-run."
  exit 1
fi

echo "Installing 4 project-scoped MCPs..."
echo

# Remove stale entries (ignore errors if not present)
for name in context7 ref-tools exa tavily; do
  claude mcp remove --scope project "$name" 2>/dev/null && echo "  removed stale: $name" || true
done
echo

# 1. Context7 — up-to-date library docs (stdio, @upstash/context7-mcp)
#    Free API key: https://context7.com/dashboard
claude mcp add --scope project context7 \
  -e CONTEXT7_API_KEY="${CONTEXT7_API_KEY}" \
  -- npx -y @upstash/context7-mcp --api-key "${CONTEXT7_API_KEY}"
echo "✓ context7 (library docs)"

# 2. Ref Tools — token-efficient documentation search (HTTP, ref.tools)
#    API key + URL: https://ref.tools dashboard → Plans or Context product
claude mcp add --transport http --scope project ref-tools \
  "${REF_MCP_URL}" \
  --header "x-ref-api-key: ${REF_API_KEY}"
echo "✓ ref-tools (documentation search)"

# 3. Exa — neural semantic web search (stdio, exa-mcp-server)
#    API key: https://dashboard.exa.ai/api-keys
claude mcp add --scope project exa \
  -e EXA_API_KEY="${EXA_API_KEY}" \
  -- npx -y exa-mcp-server
echo "✓ exa (semantic search)"

# 4. Tavily — AI-optimised web search (stdio, tavily-mcp)
#    API key: https://app.tavily.com/home
claude mcp add --scope project tavily \
  -e TAVILY_API_KEY="${TAVILY_API_KEY}" \
  -- npx -y tavily-mcp@latest
echo "✓ tavily (web search)"

echo
echo "All 4 MCPs installed. Verify with:"
echo "  claude mcp list"
