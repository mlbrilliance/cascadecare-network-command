#!/usr/bin/env bash
# Rasterize docs/images/architecture.svg -> architecture.png via headless Chrome.
# Runs under WSL using the Windows Chrome binary (full SVG-filter fidelity).
# Build-time tooling only.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMG_DIR="$REPO_DIR/docs/images"
CHROME="${CHROME:-/mnt/c/Program Files/Google/Chrome/Application/chrome.exe}"

W=1680
H=1150
SCALE="${SCALE:-1.5}"   # device-scale-factor: 1.5 = retina-crisp at the README's 900px display

# Translate the WSL path to a Windows path for chrome.exe.
WIN_IMG_DIR="$(wslpath -w "$IMG_DIR" 2>/dev/null || echo "$IMG_DIR")"

# Wrap the SVG in a zero-margin HTML host so Chrome renders at exact dimensions.
cat > "$IMG_DIR/_arch_host.html" <<EOF
<!doctype html><html><head><meta charset="utf-8">
<style>html,body{margin:0;padding:0;background:transparent}svg{display:block}</style>
</head><body>
$(cat "$IMG_DIR/architecture.svg")
</body></html>
EOF

"$CHROME" --headless --disable-gpu --hide-scrollbars \
  --force-device-scale-factor="${SCALE}" \
  --default-background-color=00000000 \
  --window-size="${W},${H}" \
  --screenshot="${WIN_IMG_DIR}\\architecture.png" \
  "file:///${WIN_IMG_DIR//\\//}/_arch_host.html" >/dev/null 2>&1

rm -f "$IMG_DIR/_arch_host.html"
echo "rendered $IMG_DIR/architecture.png"
file "$IMG_DIR/architecture.png"
