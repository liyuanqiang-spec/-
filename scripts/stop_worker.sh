#!/usr/bin/env bash
set -euo pipefail

LABEL="com.codex.github-supervised-worker"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"

if launchctl print "gui/$UID/$LABEL" >/dev/null 2>&1; then
  launchctl bootout "gui/$UID" "$PLIST" >/dev/null 2>&1 || launchctl bootout "gui/$UID/$LABEL" >/dev/null 2>&1 || true
  echo "worker stopped: $LABEL"
else
  echo "worker not running: $LABEL"
fi

echo "logs and data preserved"
