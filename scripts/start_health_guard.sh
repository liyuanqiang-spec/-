#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LABEL="com.codex.github-worker-health-guard"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
SUPPORT_DIR="$HOME/Library/Application Support/CodexGithubWorker"
LAUNCH_LOG_DIR="$HOME/Library/Logs/CodexGithubWorker"
ENTRY="$SUPPORT_DIR/worker_health_guard_entry.sh"
LAUNCH_LOG="$LAUNCH_LOG_DIR/worker_health_guard.log"
INTERVAL_SECONDS="${WORKER_HEALTH_GUARD_INTERVAL_SECONDS:-900}"

mkdir -p "$HOME/Library/LaunchAgents" "$SUPPORT_DIR" "$LAUNCH_LOG_DIR"
touch "$LAUNCH_LOG"

cat > "$ENTRY" <<ENTRY
#!/usr/bin/env bash
set -euo pipefail
export PATH="\$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:\${PATH:-}"
export CODEX_WORKER_ROOT="$ROOT"
cd "$ROOT"
exec /bin/bash "$ROOT/scripts/worker_health_guard.sh"
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
  <key>StartInterval</key>
  <integer>$INTERVAL_SECONDS</integer>
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

launchctl enable "gui/$UID/$LABEL" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$UID" "$PLIST"
launchctl kickstart -k "gui/$UID/$LABEL" >/dev/null 2>&1 || true
echo "health guard started: $LABEL interval=${INTERVAL_SECONDS}s log=$ROOT/logs/worker_health_guard.log launch_log=$LAUNCH_LOG"
