#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LABEL="com.codex.github-supervised-worker"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
WORKER_REPO="$HOME/Library/Application Support/CodexGithubWorker/repo"
LOG="$ROOT/logs/worker.log"
HEARTBEAT="$ROOT/logs/worker_heartbeat.json"
LOCK_DIR="$ROOT/logs/worker.lock"

status="OK"

line() {
  printf '%s\n' "$*"
}

warn() {
  status="WARN"
  line "WARN: $*"
}

fail() {
  status="FAIL"
  line "FAIL: $*"
}

line "worker_health_check"
line "root=$ROOT"
line "label=$LABEL"

for path in AGENTS.md TASK_QUEUE.md STATUS.md RUN_LOG.md DECISION_REQUIRED.md scripts/codex_worker.sh; do
  if [ -e "$ROOT/$path" ]; then
    line "file_ok=$path"
  else
    fail "missing required file $path"
  fi
done

if grep -q 'WORKER_INTERVAL_SECONDS:-60' "$ROOT/scripts/codex_worker.sh" && grep -q 'WORKER_INTERVAL_SECONDS:-60' "$ROOT/scripts/start_worker.sh"; then
  line "repo_interval_seconds=60"
else
  fail "repo worker interval is not configured to 60 seconds"
fi

if [ -f "$PLIST" ]; then
  plist_interval="$(awk '/<key>StartInterval<\/key>/ {getline; gsub(/.*<integer>|<\/integer>.*/, ""); print; exit}' "$PLIST" || true)"
  line "launchd_plist=$PLIST"
  line "launchd_plist_interval=${plist_interval:-unknown}"
  if [ "${plist_interval:-}" != "60" ]; then
    warn "active launchd plist may still need reload through scripts/start_worker.sh"
  fi
else
  warn "launchd plist not found at $PLIST"
fi

if launchctl print "gui/$UID/$LABEL" >/dev/null 2>&1; then
  launch_state="$(launchctl print "gui/$UID/$LABEL" 2>/dev/null | awk -F' = ' '/state =/ {print $2; exit}' || true)"
  line "launchd_state=${launch_state:-unknown}"
else
  warn "launchd job is not currently loaded"
fi

if [ -f "$LOG" ]; then
  line "worker_log=$LOG"
else
  warn "worker log has not been created yet"
fi

if [ -f "$HEARTBEAT" ]; then
  line "heartbeat=$HEARTBEAT"
  python3 - "$HEARTBEAT" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(f"heartbeat_timestamp={payload.get('timestamp', 'unknown')}")
print(f"heartbeat_state={payload.get('state', 'unknown')}")
print(f"heartbeat_interval_seconds={payload.get('interval_seconds', 'unknown')}")
print(f"heartbeat_safety_mode={payload.get('safety_mode', 'unknown')}")
PY
else
  warn "heartbeat file has not been created yet"
fi

if [ -d "$LOCK_DIR" ]; then
  lock_pid="$(cat "$LOCK_DIR/pid" 2>/dev/null || true)"
  if [ -n "$lock_pid" ] && kill -0 "$lock_pid" 2>/dev/null; then
    warn "worker lock is active pid=$lock_pid"
  else
    warn "worker lock exists but pid is not active"
  fi
else
  line "lock_state=clear"
fi

for script in scripts/codex_worker.sh scripts/start_worker.sh scripts/stop_worker.sh scripts/worker_launchd_entry.sh; do
  if bash -n "$ROOT/$script"; then
    line "bash_syntax_ok=$script"
  else
    fail "bash syntax failed for $script"
  fi
done

if WORKER_NO_GIT_MUTATION=1 WORKER_SKIP_PULL=1 WORKER_SKIP_REMOTE_CHECK=1 WORKER_SKIP_STATE_WRITES=1 "$ROOT/scripts/codex_worker.sh" --dry-run >/tmp/codex_worker_health_dry_run.out 2>/tmp/codex_worker_health_dry_run.err; then
  line "dry_run=ok"
else
  fail "worker dry-run failed"
  sed 's/^/dry_run_stderr=/' /tmp/codex_worker_health_dry_run.err
fi

line "overall=$status"
if [ "$status" = "FAIL" ]; then
  exit 1
fi
