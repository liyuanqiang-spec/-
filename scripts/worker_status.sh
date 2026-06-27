#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="$ROOT/.codex_worker.pid"
LABEL="com.codex.github-supervised-worker"
WORKER_REPO="$HOME/Library/Application Support/CodexGithubWorker/repo"
LOG_FILE="$WORKER_REPO/logs/worker.log"
LAUNCH_LOG="$HOME/Library/Logs/CodexGithubWorker/worker.log"

if launchctl print "gui/$UID/$LABEL" >/dev/null 2>&1; then
  STATE="$(launchctl print "gui/$UID/$LABEL" 2>/dev/null | awk -F' = ' '/state =/ {print $2; exit}')"
  if [ "${STATE:-unknown}" = "running" ]; then
    echo "RUNNING launchagent=$LABEL state=$STATE worker_repo=$WORKER_REPO log=$LOG_FILE launch_log=$LAUNCH_LOG"
  else
    echo "SCHEDULED launchagent=$LABEL state=${STATE:-unknown} worker_repo=$WORKER_REPO log=$LOG_FILE launch_log=$LAUNCH_LOG"
  fi
elif [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "RUNNING pid=$(cat "$PID_FILE")"
else
  echo "STOPPED"
fi
