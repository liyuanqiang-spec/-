#!/usr/bin/env bash
set -euo pipefail

ROOT="${CODEX_WORKER_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
REFRESH_SECONDS="${SUPERVISOR_CONVERSATION_REFRESH_SECONDS:-5}"

while true; do
  clear
  printf 'GPT 和 Codex 对话可视窗口\n'
  printf '刷新间隔: %ss\n' "$REFRESH_SECONDS"
  printf '仓库: %s\n' "$ROOT"
  printf '时间: %s\n\n' "$(date '+%Y-%m-%d %H:%M:%S %z')"
  python3 "$ROOT/scripts/render_supervisor_conversation.py" --root "$ROOT" --stdout 2>/dev/null \
    || printf '对话视图暂时无法刷新，请查看 %s\n' "$ROOT/GPT_CODEX_CONVERSATION.md"
  printf '\n这个窗口只显示 GPT/Codex 之间的任务和反馈，不会重复执行任务。按 Ctrl+C 关闭窗口。\n'
  sleep "$REFRESH_SECONDS"
done
