#!/usr/bin/env bash
set -euo pipefail

ROOT="${CODEX_WORKER_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
WORKER_LABEL="com.codex.github-supervised-worker"
LOG="$ROOT/logs/worker_health_guard.log"

mkdir -p "$ROOT/logs"

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S %z')" "$*" | tee -a "$LOG"
}

worker_running() {
  launchctl print "gui/$UID/$WORKER_LABEL" >/dev/null 2>&1
}

health_check_ok() {
  /bin/bash "$ROOT/scripts/check_worker_health.sh" >> "$LOG" 2>&1
}

restart_worker() {
  log "restarting worker"
  /bin/bash "$ROOT/scripts/stop_worker.sh" >> "$LOG" 2>&1 || true
  /bin/bash "$ROOT/scripts/start_worker.sh" >> "$LOG" 2>&1
}

log "health guard check started root=$ROOT"

if ! worker_running; then
  log "worker launchd service is not running"
  restart_worker
elif ! health_check_ok; then
  log "worker health check failed"
  restart_worker
fi

if worker_running && health_check_ok; then
  log "health guard check passed"
  exit 0
fi

log "health guard could not restore worker"
exit 1
