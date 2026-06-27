#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LABEL="com.codex.quant.worker"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
INTERVAL="${WORKER_INTERVAL_SECONDS:-300}"
SUPPORT_DIR="$HOME/Library/Application Support/CodexQuantWorker"
LOG_DIR="$HOME/Library/Logs/CodexQuantWorker"
ENTRY_SCRIPT="$SUPPORT_DIR/worker_entry.sh"
OUT_FILE="$LOG_DIR/worker.out"
ERR_FILE="$LOG_DIR/worker.err"

mkdir -p "$HOME/Library/LaunchAgents"
mkdir -p "$SUPPORT_DIR" "$LOG_DIR"

if launchctl print "gui/$UID/$LABEL" >/dev/null 2>&1; then
  launchctl kickstart -k "gui/$UID/$LABEL" >/dev/null 2>&1 || true
  echo "Codex worker already registered: $LABEL"
  exit 0
fi

cat > "$ENTRY_SCRIPT" <<ENTRY
#!/usr/bin/env bash
set -euo pipefail

export PATH="/Users/zhoujiali/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
cd "$ROOT"
exec python3 -m src.codex_quant.worker --once
ENTRY
chmod +x "$ENTRY_SCRIPT"

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
    <string>$ENTRY_SCRIPT</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>StartInterval</key>
  <integer>$INTERVAL</integer>
  <key>StandardOutPath</key>
  <string>$OUT_FILE</string>
  <key>StandardErrorPath</key>
  <string>$ERR_FILE</string>
</dict>
</plist>
PLIST

launchctl bootstrap "gui/$UID" "$PLIST"
launchctl kickstart -k "gui/$UID/$LABEL" >/dev/null 2>&1 || true
echo "Codex worker launch agent scheduled: $LABEL interval=${INTERVAL}s"
