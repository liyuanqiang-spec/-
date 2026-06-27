#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="$ROOT/.codex_worker.pid"
LABEL="com.codex.quant.worker"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"

if launchctl print "gui/$UID/$LABEL" >/dev/null 2>&1; then
  launchctl bootout "gui/$UID" "$PLIST" >/dev/null 2>&1 || launchctl bootout "gui/$UID/$LABEL" >/dev/null 2>&1 || true
  echo "Codex worker stopped: $LABEL"
else
  echo "Codex worker launch agent is not running."
fi

if [ -f "$PID_FILE" ]; then
  PID="$(cat "$PID_FILE")"
  if kill -0 "$PID" 2>/dev/null; then
    kill "$PID" || true
  fi
  rm -f "$PID_FILE"
fi
