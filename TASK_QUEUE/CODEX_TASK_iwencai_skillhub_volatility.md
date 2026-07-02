# CODEX_TASK_iwencai_skillhub_volatility

Created: 2026-07-02
Marker: `IWENCAI_SKILLHUB_VOLATILITY_EXPORT_20260702`

## Objective

Use the local Mac mini Codex worker route to install Iwencai SkillHub CLI-only if missing, then install the SkillHub skill named `波动率策略`, then export the installed skill package for ChatGPT to install offline.

This is a local tooling / skill installation task only. It is not a trading task.

## Safety constraints

- Keep `PHASE_1_SIMULATION_ONLY`.
- Do not connect to brokers.
- Do not log in to 同花顺 / 问财 accounts.
- Do not read, print, commit, or expose secrets, tokens, passwords, cookies, API keys, browser profiles, or local private configuration.
- Do not place, cancel, modify, or simulate live orders.
- Do not move funds.
- Do not use `danger-full-access`.
- If network access to Iwencai/SkillHub is blocked, stop cleanly and write a blocker status.

## Commands to run

Run from repository root on the local Mac mini worker:

```bash
set -euo pipefail

MARKER="IWENCAI_SKILLHUB_VOLATILITY_EXPORT_20260702"
SKILLS_DIR="${HOME}/.codex/skills"
EXPORT_DIR="${PWD}/skillhub_export"
EXPORT_TGZ="${EXPORT_DIR}/iwencai_skillhub_skills_export.tar.gz"
REPORT_FILE="${EXPORT_DIR}/iwencai_skillhub_install_report.md"

mkdir -p "$SKILLS_DIR" "$EXPORT_DIR"

{
  echo "# Iwencai SkillHub Volatility Skill Install Report"
  echo
  echo "Marker: \`$MARKER\`"
  echo "Started: $(date '+%Y-%m-%d %H:%M:%S %z')"
  echo
} > "$REPORT_FILE"

echo "== 1. Check skillhub CLI ==" | tee -a "$REPORT_FILE"

if ! command -v skillhub >/dev/null 2>&1; then
  echo "skillhub CLI not found. Installing CLI-only..." | tee -a "$REPORT_FILE"

  if curl -fsSL https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/install/install.sh | bash -s -- --cli-only; then
    echo "CLI install script completed." | tee -a "$REPORT_FILE"
  else
    echo "BLOCKER: CLI installer failed from Tencent COS endpoint." | tee -a "$REPORT_FILE"
    echo "Status marker: IWENCAI_SKILLHUB_CLI_INSTALL_BLOCKED" | tee -a "$REPORT_FILE"
    exit 20
  fi

  export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$HOME/.bun/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

  if ! command -v skillhub >/dev/null 2>&1; then
    FOUND_SKILLHUB="$(find "$HOME" /opt /usr/local -type f -name skillhub 2>/dev/null | head -n 1 || true)"
    if [ -n "$FOUND_SKILLHUB" ]; then
      export PATH="$(dirname "$FOUND_SKILLHUB"):$PATH"
    fi
  fi
fi

if ! command -v skillhub >/dev/null 2>&1; then
  echo "BLOCKER: skillhub command still unavailable after install attempt." | tee -a "$REPORT_FILE"
  echo "Status marker: IWENCAI_SKILLHUB_CLI_NOT_FOUND" | tee -a "$REPORT_FILE"
  exit 21
fi

{
  echo
  echo "== 2. CLI version =="
  command -v skillhub
  SKILLHUB_SKIP_SELF_UPGRADE=1 skillhub --version || skillhub --version || true
} | tee -a "$REPORT_FILE"

{
  echo
  echo "== 3. Install skill: 波动率策略 =="
} | tee -a "$REPORT_FILE"

if SKILLHUB_SKIP_SELF_UPGRADE=1 skillhub install "波动率策略" --dir "$SKILLS_DIR" --force; then
  echo "Skill install command completed." | tee -a "$REPORT_FILE"
else
  echo "BLOCKER: skillhub install failed for 波动率策略." | tee -a "$REPORT_FILE"
  echo "Status marker: IWENCAI_VOLATILITY_SKILL_INSTALL_BLOCKED" | tee -a "$REPORT_FILE"
  SKILLHUB_SKIP_SELF_UPGRADE=1 skillhub list --dir "$SKILLS_DIR" >> "$REPORT_FILE" 2>&1 || true
  exit 22
fi

{
  echo
  echo "== 4. Installed skills list =="
  SKILLHUB_SKIP_SELF_UPGRADE=1 skillhub list --dir "$SKILLS_DIR" || true
  echo
  echo "== 5. Skills tree preview =="
  find "$SKILLS_DIR" -maxdepth 4 -type f | sed "s|$SKILLS_DIR/||" | head -200
} | tee -a "$REPORT_FILE"

{
  echo
  echo "== 6. Export skills directory =="
} | tee -a "$REPORT_FILE"

tar -C "$SKILLS_DIR" -czf "$EXPORT_TGZ" .

{
  echo "Export file: $EXPORT_TGZ"
  ls -lh "$EXPORT_TGZ"
  echo
  echo "SHA256:"
  shasum -a 256 "$EXPORT_TGZ" 2>/dev/null || sha256sum "$EXPORT_TGZ" 2>/dev/null || true
  echo
  echo "Completed: $(date '+%Y-%m-%d %H:%M:%S %z')"
  echo "Result marker: IWENCAI_SKILLHUB_VOLATILITY_SKILL_EXPORTED_20260702"
} | tee -a "$REPORT_FILE"
```

## Required repository updates after execution

Commit and push these files if available:

- `skillhub_export/iwencai_skillhub_install_report.md`
- `skillhub_export/iwencai_skillhub_skills_export.tar.gz`
- Updated `TASK_QUEUE.md`
- Updated `STATUS.md`
- Updated `RUN_LOG.md`
- Updated `GPT_VISIBLE_STATUS.md` if present
- Updated `GPT_CODEX_CONVERSATION.md` if present

## Completion markers

On success, visible status files must include:

```text
IWENCAI_SKILLHUB_VOLATILITY_SKILL_EXPORTED_20260702
```

On failure, visible status files must include one of:

```text
IWENCAI_SKILLHUB_CLI_INSTALL_BLOCKED
IWENCAI_SKILLHUB_CLI_NOT_FOUND
IWENCAI_VOLATILITY_SKILL_INSTALL_BLOCKED
```

Also include a concise reason: DNS failed, connection timed out, installer failed, skill slug not found, or risk scanner blocked.
