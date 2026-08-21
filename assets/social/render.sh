#!/usr/bin/env bash
# Render social HTML templates to PNG via headless Chrome.
#
# Usage:
#   ./render.sh tpl-workflow-receipt.html [more.html ...]
#   ./render.sh --all          # every tpl-*.html and ig-*.html
#
# Each template declares its own canvas size in `html, body { width: ...px;
# height: ...px }` — the script reads that, so new sizes need no script change.
set -euo pipefail

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[[ -x "$CHROME" ]] || { echo "Chrome not found at $CHROME" >&2; exit 1; }

cd "$(dirname "$0")"

files=()
if [[ "${1:-}" == "--all" ]]; then
  files=(tpl-*.html ig-*.html gw-*.html)
else
  files=("$@")
fi
[[ ${#files[@]} -gt 0 ]] || { echo "usage: render.sh <file.html ...> | --all" >&2; exit 1; }

for f in "${files[@]}"; do
  [[ "$f" == "ig-base.css" ]] && continue
  size=$(grep -oE 'width: *[0-9]+px; *height: *[0-9]+px' "$f" | head -1 | grep -oE '[0-9]+' | paste -sd, -)
  if [[ -z "$size" ]]; then
    echo "skip $f: no 'html, body { width; height }' declaration found" >&2
    continue
  fi
  out="${f%.html}.png"
  # virtual-time-budget gives Google Fonts time to load before the shot
  "$CHROME" --headless --disable-gpu --hide-scrollbars --virtual-time-budget=10000 \
    --window-size="$size" --screenshot="$out" "file://$PWD/$f" 2>/dev/null
  echo "rendered $out ($size)"
done
