#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
QUEUE="$ROOT/TASK_QUEUE.md"
STATUS="$ROOT/STATUS.md"
RUN_LOG="$ROOT/RUN_LOG.md"
DECISION="$ROOT/DECISION_REQUIRED.md"
LOG="$ROOT/logs/worker.log"
TASK_FILE="$ROOT/logs/worker_task.txt"
INTERVAL_SECONDS="${WORKER_INTERVAL_SECONDS:-300}"
EXPECTED_REMOTE="https://github.com/liyuanqiang-spec/-.git"

mkdir -p "$ROOT/logs"
touch "$LOG"

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S %z')" "$*" | tee -a "$LOG"
}

append_decision() {
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
  {
    printf '\n## Worker Update %s\n\n' "$(date '+%Y-%m-%d %H:%M:%S %z')"
    printf 'Status: `%s`\n\n' "$1"
    printf -- '- Detail: %s\n' "$2"
    printf -- '- Safety mode: `PHASE_1_SIMULATION_ONLY`\n'
  } >> "$STATUS"
}

append_run_log() {
  {
    printf '\n## %s\n\n' "$(date '+%Y-%m-%d %H:%M:%S %z')"
    printf -- '- Event: %s\n' "$1"
    printf -- '- Detail: %s\n' "$2"
  } >> "$RUN_LOG"
}

remote_ok() {
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
out.write_text("", encoding="utf-8")
raise SystemExit(1)
PY
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

run_once() {
  cd "$ROOT"
  log "worker run started"

  if ! remote_ok; then
    append_decision "Git remote is not $EXPECTED_REMOTE"
    append_status "BLOCKED_REMOTE" "Git remote mismatch"
    append_run_log "blocked" "Git remote mismatch"
    return 1
  fi

  git pull --ff-only origin main >> "$LOG" 2>&1 || {
    append_decision "git pull failed; manual conflict/auth check required"
    append_status "BLOCKED_PULL" "git pull failed"
    append_run_log "blocked" "git pull failed"
    return 1
  }

  if ! task_id="$(extract_first_task)"; then
    log "no pending task"
    return 0
  fi

  log "selected task $task_id"

  if has_hard_stop_risk; then
    append_decision "Task $task_id contains a blocked trading/fund/secret/deletion/danger risk"
    update_task_status "$task_id" "decision_required" "blocked by risk control"
    append_status "DECISION_REQUIRED" "Task $task_id blocked by risk control"
    append_run_log "blocked" "Task $task_id blocked by risk control"
    git add TASK_QUEUE.md STATUS.md RUN_LOG.md DECISION_REQUIRED.md
    git commit -m "Block unsafe worker task $task_id" >> "$LOG" 2>&1 || true
    git push origin main >> "$LOG" 2>&1 || true
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
    git add TASK_QUEUE.md STATUS.md RUN_LOG.md DECISION_REQUIRED.md
    if ! git diff --cached --quiet; then
      git commit -m "Worker completed GPT handshake $task_id" >> "$LOG" 2>&1 || true
      git push origin main >> "$LOG" 2>&1 || {
        append_decision "git push failed after GPT handshake task $task_id"
        append_status "BLOCKED_PUSH" "git push failed after GPT handshake task $task_id"
        append_run_log "blocked" "git push failed after GPT handshake task $task_id"
        return 1
      }
    fi
    return 0
  fi

  update_task_status "$task_id" "running" "worker started"
  append_status "WORKER_RUNNING" "Task $task_id started"
  append_run_log "started" "Task $task_id started"

  prompt="Read AGENTS.md and TASK_QUEUE.md. Execute only task $task_id from TASK_QUEUE.md. Stay in PHASE_1_SIMULATION_ONLY. Do not connect real trading accounts. Do not place or cancel real orders. Do not transfer funds. Do not delete original data. Do not expose secrets. Do not use danger-full-access. Update STATUS.md and RUN_LOG.md with the result."

  if codex exec --sandbox workspace-write -C "$ROOT" "$prompt" >> "$LOG" 2>&1; then
    update_task_status "$task_id" "completed" "codex exec completed"
    append_status "WORKER_COMPLETED" "Task $task_id completed"
    append_run_log "completed" "Task $task_id completed"
  else
    update_task_status "$task_id" "failed" "codex exec failed"
    append_status "WORKER_FAILED" "Task $task_id failed; see logs/worker.log"
    append_run_log "failed" "Task $task_id failed; see logs/worker.log"
  fi

  git add AGENTS.md TASK_QUEUE.md STATUS.md RUN_LOG.md DECISION_REQUIRED.md RISK_CONTROL.md README.md PROJECT_PLAN.md DATA_SCHEMA.md DATA REPORTS scripts logs src tests data reports .gitignore
  if ! git diff --cached --quiet; then
    git commit -m "Worker processed $task_id" >> "$LOG" 2>&1 || true
    git push origin main >> "$LOG" 2>&1 || {
      append_decision "git push failed after worker processed $task_id"
      append_status "BLOCKED_PUSH" "git push failed after worker processed $task_id"
      append_run_log "blocked" "git push failed after worker processed $task_id"
      return 1
    }
  fi
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
      sleep "$INTERVAL_SECONDS"
    done
    ;;
  *)
    echo "Usage: $0 [--once|--dry-run|--loop]" >&2
    exit 2
    ;;
esac
