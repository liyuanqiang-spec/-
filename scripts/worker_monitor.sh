#!/usr/bin/env bash
set -euo pipefail

ROOT="${CODEX_WORKER_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
SUPPORT_LOG="$ROOT/logs/worker.log"
LAUNCH_LOG="$HOME/Library/Logs/CodexGithubWorker/worker.log"
REFRESH_SECONDS="${WORKER_MONITOR_REFRESH_SECONDS:-5}"

print_file_section() {
  local title="$1"
  local path="$2"
  local lines="${3:-80}"
  printf '\n## %s\n' "$title"
  if [ -f "$path" ]; then
    tail -n "$lines" "$path"
  else
    printf 'not found: %s\n' "$path"
  fi
}

print_status_summary() {
  printf 'Codex 后台执行监控窗口\n'
  printf '刷新间隔: %ss\n' "$REFRESH_SECONDS"
  printf '仓库: %s\n' "$ROOT"
  printf '时间: %s\n' "$(date '+%Y-%m-%d %H:%M:%S %z')"
  printf '最新提交: '
  git -C "$ROOT" log -1 --format='%h %cs %s' 2>/dev/null || printf 'unknown\n'
}

while true; do
  clear
  python3 "$ROOT/scripts/render_supervisor_conversation.py" --root "$ROOT" --output "$ROOT/GPT_CODEX_CONVERSATION.md" >/dev/null 2>&1 || true
  print_status_summary
  print_file_section "GPT_VISIBLE_STATUS.md" "$ROOT/GPT_VISIBLE_STATUS.md" 80
  print_file_section "GPT/Codex 对话" "$ROOT/GPT_CODEX_CONVERSATION.md" 90
  print_file_section "WORKER_DASHBOARD.md" "$ROOT/WORKER_DASHBOARD.md" 80
  print_file_section "TASK_QUEUE.md 最新任务" "$ROOT/TASK_QUEUE.md" 90
  print_file_section "本机 worker 日志" "$SUPPORT_LOG" 60
  print_file_section "launchd 启动日志" "$LAUNCH_LOG" 30
  printf '\n这个窗口只显示后台执行情况，不会重复执行任务。按 Ctrl+C 关闭窗口。\n'
  sleep "$REFRESH_SECONDS"
done
