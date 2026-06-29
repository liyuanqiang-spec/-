#!/usr/bin/env bash
set -euo pipefail

LABEL="com.codex.github-worker-health-guard"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"

if launchctl print "gui/$UID/$LABEL" >/dev/null 2>&1; then
  launchctl bootout "gui/$UID" "$PLIST" >/dev/null 2>&1 || launchctl bootout "gui/$UID/$LABEL" >/dev/null 2>&1 || true
  echo "health guard stopped: $LABEL"
else
  echo "health guard already stopped: $LABEL"
fi
