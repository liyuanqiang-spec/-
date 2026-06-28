#!/usr/bin/env bash
set -euo pipefail

ROOT="${CODEX_WORKER_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
MONITOR="$ROOT/scripts/worker_monitor.sh"

if [ ! -x "$MONITOR" ]; then
  chmod +x "$MONITOR"
fi

osascript <<OSA
tell application "Terminal"
  do script "cd $(printf '%q' "$ROOT"); $(printf '%q' "$MONITOR")"
  activate
end tell
OSA
