#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LABEL="com.codex.github-supervised-worker"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
SUPPORT_DIR="$HOME/Library/Application Support/CodexGithubWorker"
LAUNCH_LOG_DIR="$HOME/Library/Logs/CodexGithubWorker"
WORKER_REPO="$SUPPORT_DIR/repo"
LOG="$WORKER_REPO/logs/worker.log"
ENTRY="$SUPPORT_DIR/worker_entry.sh"
LAUNCH_LOG="$LAUNCH_LOG_DIR/worker.log"
ACTIVE_INTERVAL="${WORKER_ACTIVE_POLL_SECONDS:-${WORKER_ACTIVE_POLL_INTERVAL_SECONDS:-30}}"
WARM_INTERVAL="${WORKER_WARM_POLL_SECONDS:-${WORKER_WARM_POLL_INTERVAL_SECONDS:-60}}"
IDLE_INTERVAL="${WORKER_IDLE_POLL_SECONDS:-${WORKER_IDLE_POLL_INTERVAL_SECONDS:-600}}"
IDLE_BACKOFF_AFTER_CHECKS="${WORKER_IDLE_BACKOFF_AFTER_CHECKS:-5}"
WARM_CHECKS_AFTER_ACTIVITY="${WORKER_WARM_CHECKS_AFTER_ACTIVITY:-3}"
DEFAULT_HTTP_PROXY="${WORKER_HTTP_PROXY:-${HTTP_PROXY:-http://127.0.0.1:10090}}"
DEFAULT_HTTPS_PROXY="${WORKER_HTTPS_PROXY:-${HTTPS_PROXY:-$DEFAULT_HTTP_PROXY}}"
DEFAULT_ALL_PROXY="${WORKER_ALL_PROXY:-${ALL_PROXY:-socks5://127.0.0.1:10090}}"
REMOTE_URL="https://github.com/liyuanqiang-spec/-.git"

export HTTP_PROXY="$DEFAULT_HTTP_PROXY"
export HTTPS_PROXY="$DEFAULT_HTTPS_PROXY"
export ALL_PROXY="$DEFAULT_ALL_PROXY"
export http_proxy="$DEFAULT_HTTP_PROXY"
export https_proxy="$DEFAULT_HTTPS_PROXY"
export all_proxy="$DEFAULT_ALL_PROXY"

mkdir -p "$HOME/Library/LaunchAgents" "$SUPPORT_DIR" "$LAUNCH_LOG_DIR"
touch "$LAUNCH_LOG"

if [ ! -d "$WORKER_REPO/.git" ]; then
  rm -rf "$WORKER_REPO"
  git clone "$REMOTE_URL" "$WORKER_REPO"
else
  git -C "$WORKER_REPO" pull --ff-only origin main
fi

mkdir -p "$WORKER_REPO/logs"
touch "$LOG"

cat > "$ENTRY" <<ENTRY
#!/usr/bin/env bash
set -euo pipefail
export PATH="\$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:\${PATH:-}"
export CODEX_WORKER_ROOT="$WORKER_REPO"
export WORKER_ACTIVE_POLL_SECONDS="$ACTIVE_INTERVAL"
export WORKER_WARM_POLL_SECONDS="$WARM_INTERVAL"
export WORKER_IDLE_POLL_SECONDS="$IDLE_INTERVAL"
export WORKER_ACTIVE_POLL_INTERVAL_SECONDS="$ACTIVE_INTERVAL"
export WORKER_WARM_POLL_INTERVAL_SECONDS="$WARM_INTERVAL"
export WORKER_IDLE_POLL_INTERVAL_SECONDS="$IDLE_INTERVAL"
export WORKER_IDLE_BACKOFF_AFTER_CHECKS="$IDLE_BACKOFF_AFTER_CHECKS"
export WORKER_WARM_CHECKS_AFTER_ACTIVITY="$WARM_CHECKS_AFTER_ACTIVITY"
export LOCAL_REVIEW_TRIGGER_DRY_RUN_ENABLED="${LOCAL_REVIEW_TRIGGER_DRY_RUN_ENABLED:-1}"
export HTTP_PROXY="$DEFAULT_HTTP_PROXY"
export HTTPS_PROXY="$DEFAULT_HTTPS_PROXY"
export ALL_PROXY="$DEFAULT_ALL_PROXY"
export http_proxy="$DEFAULT_HTTP_PROXY"
export https_proxy="$DEFAULT_HTTPS_PROXY"
export all_proxy="$DEFAULT_ALL_PROXY"
cd "$WORKER_REPO"
exec /bin/bash "$WORKER_REPO/scripts/codex_worker.sh" --loop
ENTRY
chmod +x "$ENTRY"

cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>$ENTRY</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>$LAUNCH_LOG</string>
  <key>StandardErrorPath</key>
  <string>$LAUNCH_LOG</string>
</dict>
</plist>
PLIST

if launchctl print "gui/$UID/$LABEL" >/dev/null 2>&1; then
  launchctl bootout "gui/$UID" "$PLIST" >/dev/null 2>&1 || launchctl bootout "gui/$UID/$LABEL" >/dev/null 2>&1 || true
fi

launchctl bootstrap "gui/$UID" "$PLIST"
launchctl kickstart -k "gui/$UID/$LABEL" >/dev/null 2>&1 || true
echo "worker started: $LABEL mode=adaptive_loop active=${ACTIVE_INTERVAL}s warm=${WARM_INTERVAL}s idle=${IDLE_INTERVAL}s idle_backoff=${IDLE_BACKOFF_AFTER_CHECKS} warm_checks=${WARM_CHECKS_AFTER_ACTIVITY} log=$LOG launch_log=$LAUNCH_LOG"
