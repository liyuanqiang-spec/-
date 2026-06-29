#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATUS="PASS"
REASONS=()

fail() {
  STATUS="FAIL"
  REASONS+=("$1")
}

line() {
  printf '%s\n' "$*"
}

line "worker_health_check"
line "root=$ROOT"

for path in \
  AGENTS.md \
  TASK_QUEUE.md \
  STATUS.md \
  RUN_LOG.md \
  DECISION_REQUIRED.md \
  RISK_CONTROL.md \
  RELIABILITY_RUNBOOK.md \
  WORKER_DASHBOARD.md \
  GPT_VISIBLE_STATUS.md \
  GPT_CODEX_CONVERSATION.md \
  GPT_REVIEW.md \
  .gpt_state.json \
  scripts/refresh_visible_status.py \
  scripts/codex_worker.sh \
  scripts/start_worker.sh \
  scripts/stop_worker.sh \
  scripts/worker_health_guard.sh \
  scripts/start_health_guard.sh \
  scripts/stop_health_guard.sh \
  scripts/worker_health_status.sh \
  scripts/render_supervisor_conversation.py \
  scripts/supervisor_conversation_monitor.sh \
  scripts/open_supervisor_conversation.sh; do
  if [ -e "$ROOT/$path" ]; then
    line "file_ok=$path"
  else
    fail "missing required file $path"
  fi
done

for script in scripts/codex_worker.sh scripts/start_worker.sh scripts/stop_worker.sh scripts/worker_launchd_entry.sh scripts/check_worker_health.sh scripts/worker_health_guard.sh scripts/start_health_guard.sh scripts/stop_health_guard.sh scripts/worker_health_status.sh scripts/supervisor_conversation_monitor.sh scripts/open_supervisor_conversation.sh; do
  if [ -f "$ROOT/$script" ]; then
    if bash -n "$ROOT/$script"; then
      line "bash_syntax_ok=$script"
    else
      fail "bash syntax failed for $script"
    fi
  else
    fail "missing bash script $script"
  fi
done

if python3 - "$ROOT" <<'PY'
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

root = Path(sys.argv[1])
script = root / "scripts" / "refresh_visible_status.py"
spec = importlib.util.spec_from_file_location("refresh_visible_status", script)
if spec is None or spec.loader is None:
    print("queue_parse=failed")
    raise SystemExit(1)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
tasks = module.parse_queue_tasks((root / "TASK_QUEUE.md").read_text(encoding="utf-8"))
if not tasks:
    print("queue_parse=failed")
    raise SystemExit(1)
current = next((task for task in tasks if task.status == "running"), None) or next(
    (task for task in tasks if task.status in module.READY_STATUSES), None
)
decisions = module.unresolved_decisions((root / "DECISION_REQUIRED.md").read_text(encoding="utf-8"))
print(f"queue_parse=ok tasks={len(tasks)}")
print(f"first_pending_or_running={module.task_summary(current)}")
print(f"unresolved_decisions={len(decisions)}")
PY
then
  :
else
  fail "queue parse or decision parse failed"
fi

VISIBLE_CHECK_OUT="$(mktemp "${TMPDIR:-/tmp}/codex_visible_check.XXXXXX")"
if python3 "$ROOT/scripts/refresh_visible_status.py" --root "$ROOT" --check >"$VISIBLE_CHECK_OUT" 2>&1; then
  sed 's/^/visible_status_check=/' "$VISIBLE_CHECK_OUT"
else
  sed 's/^/visible_status_check=/' "$VISIBLE_CHECK_OUT"
  fail "visible status files are inconsistent with TASK_QUEUE.md or DECISION_REQUIRED.md"
fi
rm -f "$VISIBLE_CHECK_OUT"

if ! grep -q 'codex exec --sandbox workspace-write' "$ROOT/scripts/codex_worker.sh"; then
  fail "worker is not configured to use workspace-write"
else
  line "worker_sandbox=workspace-write"
fi

if grep -Eq 'codex exec .*--sandbox[ =](danger-full-access|dangerously-bypass)' "$ROOT/scripts/codex_worker.sh"; then
  fail "worker script uses a dangerous sandbox"
else
  line "worker_dangerous_sandbox=absent"
fi

if grep -q 'WORKER_IDLE_POLL_INTERVAL_SECONDS:-600' "$ROOT/scripts/codex_worker.sh" \
  && grep -q 'WORKER_ACTIVE_POLL_INTERVAL_SECONDS:-30' "$ROOT/scripts/codex_worker.sh" \
  && grep -q 'WORKER_WARM_POLL_INTERVAL_SECONDS:-60' "$ROOT/scripts/codex_worker.sh" \
  && grep -q 'WORKER_IDLE_POLL_INTERVAL_SECONDS:-600' "$ROOT/scripts/start_worker.sh" \
  && grep -q 'WORKER_ACTIVE_POLL_INTERVAL_SECONDS:-30' "$ROOT/scripts/start_worker.sh" \
  && grep -q 'WORKER_WARM_POLL_INTERVAL_SECONDS:-60' "$ROOT/scripts/start_worker.sh" \
  && grep -q 'default=600' "$ROOT/src/codex_quant/worker.py" \
  && grep -q 'default=30' "$ROOT/src/codex_quant/worker.py" \
  && grep -q 'default=60' "$ROOT/src/codex_quant/worker.py"; then
  line "worker_poll_intervals=active_30s_warm_60s_idle_600s"
else
  fail "worker polling defaults are not active=30 seconds, warm=60 seconds, and idle=600 seconds"
fi

if grep -q 'WORKER_NIGHT_START_HOUR:-22' "$ROOT/scripts/codex_worker.sh" \
  && grep -q 'WORKER_NIGHT_END_HOUR:-8' "$ROOT/scripts/codex_worker.sh" \
  && grep -q 'WORKER_NIGHT_WARM_POLL_INTERVAL_SECONDS:-600' "$ROOT/scripts/codex_worker.sh" \
  && grep -q 'WORKER_NIGHT_IDLE_POLL_INTERVAL_SECONDS:-1800' "$ROOT/scripts/codex_worker.sh" \
  && grep -q 'WORKER_NIGHT_START_HOUR:-22' "$ROOT/scripts/start_worker.sh" \
  && grep -q 'WORKER_NIGHT_END_HOUR:-8' "$ROOT/scripts/start_worker.sh"; then
  line "worker_night_window=22_08_warm_600s_idle_1800s"
else
  fail "worker night window defaults are not 22:00-08:00 with warm=600 seconds and idle=1800 seconds"
fi

if grep -q 'codex_worker.sh" --loop' "$ROOT/scripts/start_worker.sh"; then
  line "worker_launch_mode=adaptive_loop"
else
  fail "worker start script does not launch adaptive loop mode"
fi

if grep -q 'Refresh visible worker status' "$ROOT/scripts/codex_worker.sh"; then
  fail "idle no-pending path still refreshes visible status"
else
  line "idle_visible_status_refresh=disabled"
fi

if [ "$STATUS" = "PASS" ]; then
  line "PASS"
  exit 0
fi

line "FAIL"
for reason in "${REASONS[@]}"; do
  line "- $reason"
done
exit 1
