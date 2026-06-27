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
RUNTIME="$SUPPORT_DIR/codex_worker_runtime.sh"
LAUNCH_LOG="$LAUNCH_LOG_DIR/worker.log"
INTERVAL="${WORKER_INTERVAL_SECONDS:-300}"
REMOTE_URL="https://github.com/liyuanqiang-spec/-.git"

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
cp "$WORKER_REPO/scripts/codex_worker.sh" "$RUNTIME"
chmod +x "$RUNTIME"

cat > "$ENTRY" <<ENTRY
#!/usr/bin/env bash
set -euo pipefail
export PATH="\$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:\${PATH:-}"
export CODEX_WORKER_ROOT="$WORKER_REPO"
cd "$WORKER_REPO"
exec /bin/bash "$RUNTIME" --once
ENTRY
chmod +x "$ENTRY"

if launchctl print "gui/$UID/$LABEL" >/dev/null 2>&1; then
  launchctl kickstart -k "gui/$UID/$LABEL" >/dev/null 2>&1 || true
  echo "worker already started and kicked: $LABEL log=$LOG launch_log=$LAUNCH_LOG"
  exit 0
fi

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
  <key>StartInterval</key>
  <integer>$INTERVAL</integer>
  <key>RunAtLoad</key>
  <true/>
  <key>StandardOutPath</key>
  <string>$LAUNCH_LOG</string>
  <key>StandardErrorPath</key>
  <string>$LAUNCH_LOG</string>
</dict>
</plist>
PLIST

launchctl bootstrap "gui/$UID" "$PLIST"
launchctl kickstart -k "gui/$UID/$LABEL" >/dev/null 2>&1 || true
echo "worker started: $LABEL interval=${INTERVAL}s log=$LOG launch_log=$LAUNCH_LOG"
