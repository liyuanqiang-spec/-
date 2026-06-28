#!/usr/bin/env bash
set -euo pipefail

if [ -n "${CODEX_WORKER_ROOT:-}" ]; then
  ROOT="$CODEX_WORKER_ROOT"
else
  ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi
QUEUE="$ROOT/TASK_QUEUE.md"
STATUS="$ROOT/STATUS.md"
RUN_LOG="$ROOT/RUN_LOG.md"
DECISION="$ROOT/DECISION_REQUIRED.md"
DASHBOARD_FILE="WORKER_DASHBOARD.md"
DASHBOARD="$ROOT/$DASHBOARD_FILE"
LOG="$ROOT/logs/worker.log"
TASK_FILE="$ROOT/logs/worker_task.txt"
LOCK_DIR="$ROOT/logs/worker.lock"
HEARTBEAT="$ROOT/logs/worker_heartbeat.json"
POLL_STATE="$ROOT/logs/worker_poll_state.json"
ACTIVE_POLL_INTERVAL_SECONDS="${WORKER_ACTIVE_POLL_SECONDS:-${WORKER_ACTIVE_POLL_INTERVAL_SECONDS:-30}}"
WARM_POLL_INTERVAL_SECONDS="${WORKER_WARM_POLL_SECONDS:-${WORKER_WARM_POLL_INTERVAL_SECONDS:-60}}"
IDLE_POLL_INTERVAL_SECONDS="${WORKER_IDLE_POLL_SECONDS:-${WORKER_IDLE_POLL_INTERVAL_SECONDS:-600}}"
IDLE_BACKOFF_AFTER_CHECKS="${WORKER_IDLE_BACKOFF_AFTER_CHECKS:-5}"
WARM_CHECKS_AFTER_ACTIVITY="${WORKER_WARM_CHECKS_AFTER_ACTIVITY:-3}"
EXPECTED_REMOTE="https://github.com/liyuanqiang-spec/-.git"
GIT_TIMEOUT_SECONDS="${GIT_TIMEOUT_SECONDS:-120}"
CODEX_EXEC_TIMEOUT_SECONDS="${CODEX_EXEC_TIMEOUT_SECONDS:-1800}"
ROUND_TIMEOUT_SECONDS="${WORKER_ROUND_TIMEOUT_SECONDS:-2400}"
LOCK_STALE_SECONDS="${WORKER_LOCK_STALE_SECONDS:-3600}"
MAX_TASK_ATTEMPTS="${WORKER_MAX_TASK_ATTEMPTS:-3}"
LOCAL_REVIEW_TRIGGER_DRY_RUN_ENABLED="${LOCAL_REVIEW_TRIGGER_DRY_RUN_ENABLED:-0}"

export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:${PATH:-}"
export GIT_TERMINAL_PROMPT=0

mkdir -p "$ROOT/logs"

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S %z')" "$*" | tee -a "$LOG"
}

write_heartbeat() {
  if [ "${WORKER_SKIP_STATE_WRITES:-0}" = "1" ]; then
    return 0
  fi
  local state="$1"
  local detail="${2:-}"
  local task="${3:-none}"
  python3 - "$HEARTBEAT" "$state" "$detail" "$task" "$IDLE_POLL_INTERVAL_SECONDS" "$ACTIVE_POLL_INTERVAL_SECONDS" <<'PY'
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

path = Path(sys.argv[1])
state, detail, task, idle_interval, active_interval = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]
path.parent.mkdir(parents=True, exist_ok=True)
payload = {
    "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
    "state": state,
    "detail": detail,
    "task": task,
    "interval_seconds": int(idle_interval),
    "idle_poll_interval_seconds": int(idle_interval),
    "active_poll_interval_seconds": int(active_interval),
    "safety_mode": "PHASE_1_SIMULATION_ONLY",
}
path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
}

acquire_lock() {
  if mkdir "$LOCK_DIR" 2>/dev/null; then
    printf '%s\n' "$$" > "$LOCK_DIR/pid"
    date '+%Y-%m-%d %H:%M:%S %z' > "$LOCK_DIR/created_at"
    return 0
  fi

  local lock_pid=""
  if [ -f "$LOCK_DIR/pid" ]; then
    lock_pid="$(cat "$LOCK_DIR/pid" 2>/dev/null || true)"
  fi
  if [ -n "$lock_pid" ] && kill -0 "$lock_pid" 2>/dev/null; then
    log "another worker run is active pid=$lock_pid"
    write_heartbeat "locked" "another worker run is active pid=$lock_pid"
    return 1
  fi

  local now created age
  now="$(date +%s)"
  created="$(stat -f %m "$LOCK_DIR" 2>/dev/null || printf '0')"
  age=$((now - created))
  if [ "$age" -ge "$LOCK_STALE_SECONDS" ]; then
    log "removing stale worker lock age=${age}s"
    rm -rf "$LOCK_DIR"
    mkdir "$LOCK_DIR"
    printf '%s\n' "$$" > "$LOCK_DIR/pid"
    date '+%Y-%m-%d %H:%M:%S %z' > "$LOCK_DIR/created_at"
    return 0
  fi

  log "worker lock exists and is not stale age=${age}s"
  write_heartbeat "locked" "worker lock exists and is not stale age=${age}s"
  return 1
}

release_lock() {
  rm -rf "$LOCK_DIR"
}

run_with_timeout() {
  local timeout_seconds="$1"
  shift
  "$@" &
  local cmd_pid="$!"
  local elapsed=0
  while kill -0 "$cmd_pid" 2>/dev/null; do
    if [ "$elapsed" -ge "$timeout_seconds" ]; then
      kill "$cmd_pid" 2>/dev/null || true
      sleep 1
      kill -9 "$cmd_pid" 2>/dev/null || true
      wait "$cmd_pid" 2>/dev/null || true
      return 124
    fi
    sleep 1
    elapsed=$((elapsed + 1))
  done
  wait "$cmd_pid"
}

append_decision() {
  if [ "${WORKER_SKIP_STATE_WRITES:-0}" = "1" ]; then
    return 0
  fi
  if grep -F -- "- Item: $1" "$DECISION" >/dev/null 2>&1; then
    return 0
  fi
  {
    printf '\n## Decision Required %s\n\n' "$(date '+%Y-%m-%d %H:%M:%S %z')"
    printf -- '- Item: %s\n' "$1"
    printf -- '- Current action: worker stopped before execution\n'
    printf -- '- A 推荐: keep simulation-only and rewrite the task as safe research work\n'
    printf -- '- B: explicitly authorize the blocked setup/action\n'
    printf -- '- C: cancel this task\n'
  } >> "$DECISION"
}

append_status() {
  if [ "${WORKER_SKIP_STATE_WRITES:-0}" = "1" ]; then
    return 0
  fi
  {
    printf '\n## Worker Update %s\n\n' "$(date '+%Y-%m-%d %H:%M:%S %z')"
    printf 'Status: `%s`\n\n' "$1"
    printf -- '- Detail: %s\n' "$2"
    printf -- '- Safety mode: `PHASE_1_SIMULATION_ONLY`\n'
  } >> "$STATUS"
}

append_run_log() {
  if [ "${WORKER_SKIP_STATE_WRITES:-0}" = "1" ]; then
    return 0
  fi
  {
    printf '\n## %s\n\n' "$(date '+%Y-%m-%d %H:%M:%S %z')"
    printf -- '- Event: %s\n' "$1"
    printf -- '- Detail: %s\n' "$2"
  } >> "$RUN_LOG"
}

update_dashboard() {
  if [ "${WORKER_SKIP_STATE_WRITES:-0}" = "1" ]; then
    return 0
  fi
  if [ -f "$ROOT/scripts/refresh_visible_status.py" ]; then
    if ! python3 "$ROOT/scripts/refresh_visible_status.py" --root "$ROOT" --quiet >> "$LOG" 2>&1; then
      log "status_refresh failed"
      append_decision "worker sync failed at status_refresh stage: visible status refresh failed"
      append_status "BLOCKED_STATUS_REFRESH" "visible status refresh failed"
      append_run_log "blocked" "worker sync failed at status_refresh stage"
    fi
  elif [ -f "$ROOT/scripts/update_worker_dashboard.py" ]; then
    if ! python3 "$ROOT/scripts/update_worker_dashboard.py" >> "$LOG" 2>&1; then
      log "dashboard update failed"
      append_decision "worker sync failed at status_refresh stage: dashboard update failed"
      append_status "BLOCKED_STATUS_REFRESH" "dashboard update failed"
      append_run_log "blocked" "worker sync failed at status_refresh stage"
    fi
  fi
  return 0
}

visible_status_consistent() {
  if [ -f "$ROOT/scripts/refresh_visible_status.py" ]; then
    python3 "$ROOT/scripts/refresh_visible_status.py" --root "$ROOT" --check >/dev/null 2>&1
    return "$?"
  fi
  return 1
}

idle_heartbeat_current() {
  python3 - "$HEARTBEAT" "$IDLE_POLL_INTERVAL_SECONDS" "$ACTIVE_POLL_INTERVAL_SECONDS" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
idle_interval = int(sys.argv[2])
active_interval = int(sys.argv[3])
if not path.exists():
    raise SystemExit(1)
try:
    payload = json.loads(path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError):
    raise SystemExit(1)
if payload.get("state") != "idle":
    raise SystemExit(1)
if payload.get("task") not in {"none", None}:
    raise SystemExit(1)
if int(payload.get("idle_poll_interval_seconds", payload.get("interval_seconds", -1))) != idle_interval:
    raise SystemExit(1)
if int(payload.get("active_poll_interval_seconds", -1)) != active_interval:
    raise SystemExit(1)
raise SystemExit(0)
PY
}

git_pull_ff() {
  if [ "${WORKER_NO_GIT_MUTATION:-0}" = "1" ] || [ "${WORKER_SKIP_PULL:-0}" = "1" ]; then
    return 0
  fi
  run_with_timeout "$GIT_TIMEOUT_SECONDS" git pull --ff-only --quiet origin main
}

run_local_review_trigger_dry_run() {
  local message="$1"
  case "${LOCAL_REVIEW_TRIGGER_DRY_RUN_ENABLED}" in
    1|true|TRUE|yes|YES)
      ;;
    *)
      return 0
      ;;
  esac

  if [ ! -f "$ROOT/scripts/local_review_trigger_dry_run.py" ]; then
    append_run_log "local_review_trigger_dry_run_skipped" "script missing after successful push for $message"
    log "local review trigger dry run skipped: script missing"
    return 0
  fi

  if python3 "$ROOT/scripts/local_review_trigger_dry_run.py" --root "$ROOT" --trigger-message "$message" --quiet >> "$LOG" 2>&1; then
    append_run_log "local_review_trigger_dry_run" "LOCAL_REVIEW_TRIGGER_DRY_RUN_READY after successful push for $message"
    if [ -f "$ROOT/scripts/refresh_visible_status.py" ]; then
      python3 "$ROOT/scripts/refresh_visible_status.py" --root "$ROOT" --quiet >> "$LOG" 2>&1 || true
    fi
    log "local review trigger dry run ready after successful push for $message"
    return 0
  fi

  append_run_log "local_review_trigger_dry_run_failed" "dry-run reviewer failed after successful push for $message"
  log "local review trigger dry run failed after successful push for $message"
  return 0
}

commit_and_push() {
  local message="$1"
  shift
  local existing_paths=()
  local path
  for path in "$@"; do
    if [ -e "$ROOT/$path" ]; then
      existing_paths+=("$path")
    fi
  done
  if [ "${#existing_paths[@]}" -eq 0 ]; then
    log "no existing paths to commit for: $message"
    return 0
  fi
  if [ "${WORKER_NO_GIT_MUTATION:-0}" = "1" ]; then
    log "git add/commit/push skipped by worker verification mode: $message paths=${existing_paths[*]}"
    return 0
  fi
  git add "${existing_paths[@]}"
  if ! git diff --cached --quiet; then
    if ! git commit -m "$message" >> "$LOG" 2>&1; then
      append_decision "worker sync failed at commit stage: git commit failed for $message"
      append_status "BLOCKED_COMMIT" "git commit failed for $message"
      append_run_log "blocked" "worker sync failed at commit stage for $message"
      write_heartbeat "blocked" "git commit failed for $message"
      return 1
    fi
    if ! run_with_timeout "$GIT_TIMEOUT_SECONDS" git push origin main; then
      append_decision "worker sync failed at push stage: git push failed for $message"
      append_status "BLOCKED_PUSH" "git push failed for $message"
      append_run_log "blocked" "worker sync failed at push stage for $message"
      write_heartbeat "blocked" "git push failed for $message"
      return 1
    fi
    run_local_review_trigger_dry_run "$message"
  fi
}

remote_ok() {
  if [ "${WORKER_SKIP_REMOTE_CHECK:-0}" = "1" ]; then
    return 0
  fi
  local url
  url="$(git -C "$ROOT" remote get-url origin 2>/dev/null || true)"
  [ "$url" = "$EXPECTED_REMOTE" ] || [ "$url" = "git@github.com:liyuanqiang-spec/-.git" ]
}

extract_first_task() {
  python3 - "$QUEUE" "$TASK_FILE" <<'PY'
from pathlib import Path
import re
import sys

queue = Path(sys.argv[1])
out = Path(sys.argv[2])
text = queue.read_text(encoding="utf-8")
blocks = re.split(r"(?m)^###\s+", text)
for block in blocks[1:]:
    block = "### " + block.strip() + "\n"
    if re.search(r"(?mi)^-\s*Status:\s*(pending|queued|todo)\s*$", block):
        out.write_text(block, encoding="utf-8")
        print(block.splitlines()[0].replace("###", "").strip())
        raise SystemExit(0)
raise SystemExit(1)
PY
}

queue_has_pending() {
  python3 - "$QUEUE" <<'PY'
from pathlib import Path
import re
import sys

text = Path(sys.argv[1]).read_text(encoding="utf-8")
if re.search(r"(?mi)^-\s*Status:\s*(pending|queued|todo)\s*$", text):
    raise SystemExit(0)
raise SystemExit(1)
PY
}

unresolved_decision_count() {
  python3 - "$ROOT" <<'PY'
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

root = Path(sys.argv[1])
script = root / "scripts" / "refresh_visible_status.py"
spec = importlib.util.spec_from_file_location("refresh_visible_status", script)
if spec is None or spec.loader is None:
    print(0)
    raise SystemExit(0)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
decision_text = (root / "DECISION_REQUIRED.md").read_text(encoding="utf-8")
print(len(module.unresolved_decisions(decision_text)))
PY
}

adaptive_poll_after_round() {
  local pending=0
  local decisions=0
  if queue_has_pending; then
    pending=1
  fi
  decisions="$(unresolved_decision_count 2>/dev/null || printf '0')"

  local result interval mode changed idle_count reason
  result="$(
    python3 - "$POLL_STATE" "$HEARTBEAT" "$pending" "$decisions" \
      "$ACTIVE_POLL_INTERVAL_SECONDS" "$WARM_POLL_INTERVAL_SECONDS" "$IDLE_POLL_INTERVAL_SECONDS" \
      "$IDLE_BACKOFF_AFTER_CHECKS" "$WARM_CHECKS_AFTER_ACTIVITY" <<'PY'
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

poll_path = Path(sys.argv[1])
heartbeat_path = Path(sys.argv[2])
pending = int(sys.argv[3])
decisions = int(sys.argv[4])
active_interval = int(sys.argv[5])
warm_interval = int(sys.argv[6])
idle_interval = int(sys.argv[7])
idle_after = int(sys.argv[8])
warm_checks = int(sys.argv[9])

def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

previous = read_json(poll_path)
heartbeat = read_json(heartbeat_path)
previous_mode = str(previous.get("mode", ""))
previous_heartbeat = str(previous.get("last_heartbeat_timestamp", ""))
heartbeat_timestamp = str(heartbeat.get("timestamp", ""))
heartbeat_state = str(heartbeat.get("state", ""))
activity_states = {"selected", "running", "completed", "failed", "blocked", "timeout"}
new_activity = bool(
    heartbeat_timestamp
    and heartbeat_timestamp != previous_heartbeat
    and heartbeat_state in activity_states
)

if pending:
    mode = "ACTIVE"
    interval = active_interval
    idle_count = 0
    warm_remaining = warm_checks
    reason = "new pending safe task detected"
elif decisions:
    mode = "WARM"
    interval = warm_interval
    idle_count = 0
    warm_remaining = warm_checks
    reason = "unresolved blocker detected"
elif new_activity:
    mode = "WARM"
    interval = warm_interval
    idle_count = 0
    warm_remaining = warm_checks
    reason = f"recent worker activity: {heartbeat_state}"
else:
    previous_warm = int(previous.get("warm_remaining_checks", 0) or 0)
    warm_remaining = max(previous_warm - 1, 0)
    idle_count = int(previous.get("consecutive_idle_checks", 0) or 0) + 1
    if warm_remaining > 0:
        mode = "WARM"
        interval = warm_interval
        reason = f"warm after activity ({warm_remaining} checks left)"
    elif idle_count >= idle_after:
        mode = "IDLE"
        interval = idle_interval
        reason = f"idle backoff after {idle_count} checks"
    else:
        mode = "WARM"
        interval = warm_interval
        reason = f"idle check {idle_count}/{idle_after}"

payload = {
    "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
    "mode": mode,
    "interval_seconds": interval,
    "active_poll_seconds": active_interval,
    "warm_poll_seconds": warm_interval,
    "idle_poll_seconds": idle_interval,
    "consecutive_idle_checks": idle_count,
    "idle_backoff_after_checks": idle_after,
    "warm_remaining_checks": warm_remaining,
    "warm_checks_after_activity": warm_checks,
    "pending_safe_task": bool(pending),
    "unresolved_blockers": decisions,
    "last_heartbeat_timestamp": heartbeat_timestamp,
    "last_heartbeat_state": heartbeat_state,
    "reason": reason,
}
poll_path.parent.mkdir(parents=True, exist_ok=True)
poll_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
changed = 1 if mode != previous_mode else 0
print(f"{interval}|{mode}|{changed}|{idle_count}|{reason}")
PY
  )"

  IFS='|' read -r interval mode changed idle_count reason <<< "$result"
  if [ "${changed:-0}" = "1" ]; then
    log "adaptive polling mode=${mode:-UNKNOWN} interval=${interval:-$IDLE_POLL_INTERVAL_SECONDS}s idle_checks=${idle_count:-0} reason=${reason:-unknown}" >/dev/null
  fi
  printf '%s\n' "${interval:-$IDLE_POLL_INTERVAL_SECONDS}"
}

task_type() {
  python3 - "$TASK_FILE" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
if not path.exists():
    raise SystemExit(0)
for line in path.read_text(encoding="utf-8").splitlines():
    if line.lower().startswith("- type:"):
        print(line.split(":", 1)[1].strip().lower())
        raise SystemExit(0)
PY
}

update_task_status() {
  local task_id="$1"
  local new_status="$2"
  local result="$3"
  python3 - "$QUEUE" "$task_id" "$new_status" "$result" <<'PY'
from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
task_id, status, result = sys.argv[2], sys.argv[3], sys.argv[4]
text = path.read_text(encoding="utf-8")
lines = text.splitlines()
start = None
for idx, line in enumerate(lines):
    if re.fullmatch(rf"###\s+{re.escape(task_id)}", line.strip()):
        start = idx
        break
if start is None:
    raise SystemExit(0)
end = len(lines)
for idx in range(start + 1, len(lines)):
    if lines[idx].startswith("### "):
        end = idx
        break
for idx in range(start + 1, end):
    if re.match(r"^-\s*Status:", lines[idx], flags=re.I):
        lines[idx] = f"- Status: {status}"
    if re.match(r"^-\s*Last update:", lines[idx], flags=re.I):
        lines[idx] = "- Last update: updated by worker"
    if re.match(r"^-\s*Result:", lines[idx], flags=re.I):
        lines[idx] = f"- Result: {result}"
path.write_text("\n".join(lines) + "\n", encoding="utf-8")
PY
}

has_hard_stop_risk() {
  local text
  text="$(cat "$TASK_FILE" 2>/dev/null || true)"
  text="$(printf '%s' "$text" | sed -E 's/不真实下单//g; s/不真实撤单//g; s/不接实盘//g; s/禁止真实下单//g; s/禁止真实撤单//g; s/禁止连接真实交易账户//g; s/不连接真实交易账户//g; s/Do not place or cancel real orders//Ig; s/Do not connect real trading accounts//Ig; s/Do not use danger-full-access//Ig')"
  grep -Eiq '真实交易|真实下单|实盘|撤单|资金划转|保证金划转|删除原始数据|删除raw|API Key|api key|password|密码|token|密钥|secret|danger-full-access|dangerously-bypass|real trading|real order|cancel order|fund transfer|delete raw data' <<< "$text"
}

run_codex_task_with_retries() {
  local task_id="$1"
  local prompt="$2"
  local attempt=1
  while [ "$attempt" -le "$MAX_TASK_ATTEMPTS" ]; do
    append_run_log "attempt" "Task $task_id codex exec attempt $attempt/$MAX_TASK_ATTEMPTS"
    log "codex exec attempt $attempt/$MAX_TASK_ATTEMPTS for $task_id"
    if run_with_timeout "$CODEX_EXEC_TIMEOUT_SECONDS" codex exec --sandbox workspace-write -C "$ROOT" "$prompt" >> "$LOG" 2>&1; then
      return 0
    fi
    append_run_log "retry" "Task $task_id codex exec attempt $attempt failed"
    log "codex exec attempt $attempt failed for $task_id"
    attempt=$((attempt + 1))
  done
  return 1
}

run_once_body() {
  cd "$ROOT"
  if ! remote_ok; then
    append_decision "Git remote is not $EXPECTED_REMOTE"
    append_status "BLOCKED_REMOTE" "Git remote mismatch"
    append_run_log "blocked" "Git remote mismatch"
    update_dashboard
    return 1
  fi

  git_pull_ff >/dev/null 2>&1 || {
    append_decision "worker sync failed at pull stage: git pull failed"
    append_status "BLOCKED_PULL" "git pull failed"
    append_run_log "blocked" "worker sync failed at pull stage"
    write_heartbeat "blocked" "git pull failed"
    update_dashboard
    return 1
  }

  if ! task_id="$(extract_first_task)"; then
    return 0
  fi

  log "worker run started"
  log "selected task $task_id"
  write_heartbeat "selected" "selected task $task_id" "$task_id"

  if has_hard_stop_risk; then
    append_decision "Task $task_id contains a blocked trading/fund/secret/deletion/danger risk"
    update_task_status "$task_id" "decision_required" "blocked by risk control"
    append_status "DECISION_REQUIRED" "Task $task_id blocked by risk control"
    append_run_log "blocked" "Task $task_id blocked by risk control"
    write_heartbeat "blocked" "Task $task_id blocked by risk control" "$task_id"
    update_dashboard
    commit_and_push "Block unsafe worker task $task_id" TASK_QUEUE.md STATUS.md RUN_LOG.md DECISION_REQUIRED.md "$DASHBOARD_FILE" GPT_VISIBLE_STATUS.md .gpt_state.json GPT_REVIEW.md logs/worker_heartbeat.json >> "$LOG" 2>&1 || true
    return 1
  fi

  if [ "${1:-}" = "--dry-run" ]; then
    log "dry run selected task $task_id"
    return 0
  fi

  current_type="$(task_type || true)"
  if [ "$current_type" = "status_check" ] || [ "$current_type" = "handshake" ]; then
    update_task_status "$task_id" "completed" "GPT handshake completed by local worker"
    append_status "GPT_HANDSHAKE_OK" "Task $task_id completed by the Mac mini worker; GitHub queue -> worker -> GitHub status loop is working"
    append_run_log "gpt_handshake" "Task $task_id completed by local worker without codex exec; safety mode remained PHASE_1_SIMULATION_ONLY"
    write_heartbeat "completed" "Task $task_id completed by local worker" "$task_id"
    update_dashboard
    commit_and_push "Worker completed GPT handshake $task_id" TASK_QUEUE.md STATUS.md RUN_LOG.md DECISION_REQUIRED.md "$DASHBOARD_FILE" GPT_VISIBLE_STATUS.md .gpt_state.json GPT_REVIEW.md logs/worker_heartbeat.json >> "$LOG" 2>&1 || return 1
    return 0
  fi

  update_task_status "$task_id" "running" "worker started"
  append_status "WORKER_RUNNING" "Task $task_id started"
  append_run_log "started" "Task $task_id started"
  write_heartbeat "running" "Task $task_id started" "$task_id"
  update_dashboard
  commit_and_push "Worker started $task_id" TASK_QUEUE.md STATUS.md RUN_LOG.md DECISION_REQUIRED.md "$DASHBOARD_FILE" GPT_VISIBLE_STATUS.md .gpt_state.json GPT_REVIEW.md logs/worker_heartbeat.json >> "$LOG" 2>&1 || return 1

  prompt="Read AGENTS.md and TASK_QUEUE.md. Execute only task $task_id from TASK_QUEUE.md. Stay in PHASE_1_SIMULATION_ONLY. Do not connect real trading accounts. Do not place or cancel real orders. Do not transfer funds. Do not delete original data. Do not expose secrets. Do not use danger-full-access. Update STATUS.md and RUN_LOG.md with the result. Do not run git add, git commit, or git push inside codex exec; the outer worker will commit and push after you exit."

  if ! command -v codex >/dev/null 2>&1; then
    update_task_status "$task_id" "failed" "codex command not found in worker environment"
    append_status "WORKER_FAILED" "Task $task_id failed; codex command not found in worker environment"
    append_run_log "failed" "Task $task_id failed; codex command not found in worker environment"
  elif run_codex_task_with_retries "$task_id" "$prompt"; then
    update_task_status "$task_id" "completed" "codex exec completed"
    append_status "WORKER_COMPLETED" "Task $task_id completed"
    append_run_log "completed" "Task $task_id completed"
    write_heartbeat "completed" "Task $task_id completed" "$task_id"
  else
    update_task_status "$task_id" "failed" "codex exec failed"
    append_status "WORKER_FAILED" "Task $task_id failed; see logs/worker.log"
    append_run_log "failed" "Task $task_id failed; see logs/worker.log"
    write_heartbeat "failed" "Task $task_id failed after $MAX_TASK_ATTEMPTS attempts" "$task_id"
  fi

  update_dashboard
  commit_and_push "Worker processed $task_id" AGENTS.md TASK_QUEUE.md STATUS.md RUN_LOG.md DECISION_REQUIRED.md RISK_CONTROL.md README.md WORKER_DASHBOARD.md GPT_VISIBLE_STATUS.md GPT_REVIEW.md GPT_LOCAL_REVIEW_INPUT.md GPT_REVIEW_PACKET.md .gpt_state.json PROJECT_PLAN.md DATA_SCHEMA.md DATA REPORTS RELIABILITY_RUNBOOK.md scripts logs/worker_heartbeat.json src tests data reports .gitignore >> "$LOG" 2>&1 || return 1
}

run_once() {
  cd "$ROOT"
  if remote_ok && git_pull_ff >/dev/null 2>&1 && ! extract_first_task >/dev/null 2>&1; then
    return 0
  fi

  if ! acquire_lock; then
    return 0
  fi

  local rc=0
  run_with_timeout "$ROUND_TIMEOUT_SECONDS" run_once_body "$@" || rc="$?"
  if [ "$rc" -eq 124 ]; then
    append_status "WORKER_TIMEOUT" "Worker round exceeded ${ROUND_TIMEOUT_SECONDS}s"
    append_run_log "timeout" "Worker round exceeded ${ROUND_TIMEOUT_SECONDS}s"
    write_heartbeat "timeout" "Worker round exceeded ${ROUND_TIMEOUT_SECONDS}s"
    update_dashboard
  fi
  release_lock
  return "$rc"
}

case "${1:---once}" in
  --once)
    run_once
    ;;
  --dry-run)
    run_once --dry-run
    ;;
  --loop)
    while true; do
      run_once || true
      sleep "$(adaptive_poll_after_round)"
    done
    ;;
  *)
    echo "Usage: $0 [--once|--dry-run|--loop]" >&2
    exit 2
    ;;
esac
