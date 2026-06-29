#!/usr/bin/env bash
set -euo pipefail

ROOT="${CODEX_WORKER_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
WORKER_LABEL="com.codex.github-supervised-worker"
GUARD_LABEL="com.codex.github-worker-health-guard"
GUARD_LOG="$ROOT/logs/worker_health_guard.log"

printf 'Codex worker health status\n'
printf 'time=%s\n' "$(date '+%Y-%m-%d %H:%M:%S %z')"
printf 'root=%s\n' "$ROOT"

if launchctl print "gui/$UID/$WORKER_LABEL" >/dev/null 2>&1; then
  printf 'worker=running\n'
else
  printf 'worker=stopped\n'
fi

if launchctl print "gui/$UID/$GUARD_LABEL" >/dev/null 2>&1; then
  printf 'health_guard=running\n'
else
  printf 'health_guard=stopped\n'
fi

printf '\nlatest health guard log:\n'
if [ -f "$GUARD_LOG" ]; then
  tail -n 20 "$GUARD_LOG"
else
  printf 'not found: %s\n' "$GUARD_LOG"
fi
