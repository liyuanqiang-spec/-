#!/usr/bin/env bash
set -euo pipefail

ROOT="${CODEX_WORKER_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
MONITOR="$ROOT/scripts/worker_monitor.sh"
ROOT_ESCAPED="$(printf '%s' "$ROOT" | sed 's/\\/\\\\/g; s/"/\\"/g')"
MONITOR_ESCAPED="$(printf '%s' "$MONITOR" | sed 's/\\/\\\\/g; s/"/\\"/g')"

if [ ! -x "$MONITOR" ]; then
  chmod +x "$MONITOR"
fi

osascript <<OSA
tell application "Terminal"
  do script "cd \"$ROOT_ESCAPED\" && exec /bin/bash \"$MONITOR_ESCAPED\""
  activate
end tell
OSA
