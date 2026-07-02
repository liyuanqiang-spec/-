# CODEX_TASK_iwencai_skillhub_volatility_safe

Created: 2026-07-02
Marker: `IWENCAI_SKILLHUB_EXPORT_SAFE_20260702`

## Objective

Prepare a local SkillHub package for the skill named `波动率策略` and place the compressed result in `skillhub_export/`.

This is only a local package setup and export task.

## Mode

Keep:

```text
PHASE_1_SIMULATION_ONLY
```

## Run from repository root

```bash
set -euo pipefail

MARKER="IWENCAI_SKILLHUB_EXPORT_SAFE_20260702"
OK_MARKER="IWENCAI_SKILLHUB_EXPORT_OK_20260702"
BLOCK_MARKER="IWENCAI_SKILLHUB_SETUP_BLOCKED_20260702"
SKILLS_DIR="${HOME}/.codex/skills"
EXPORT_DIR="${PWD}/skillhub_export"
EXPORT_TGZ="${EXPORT_DIR}/iwencai_skillhub_skills_export.tar.gz"
REPORT_FILE="${EXPORT_DIR}/iwencai_skillhub_install_report.md"

mkdir -p "$SKILLS_DIR" "$EXPORT_DIR"

{
  echo "# Iwencai SkillHub Package Export Report"
  echo
  echo "Marker: \`$MARKER\`"
  echo "Started: $(date '+%Y-%m-%d %H:%M:%S %z')"
  echo
} > "$REPORT_FILE"

if ! command -v skillhub >/dev/null 2>&1; then
  echo "skillhub CLI not found. Starting CLI-only setup." | tee -a "$REPORT_FILE"
  if ! curl -fsSL https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/install/install.sh | bash -s -- --cli-only; then
    echo "$BLOCK_MARKER" | tee -a "$REPORT_FILE"
    echo "Reason: CLI setup endpoint not reachable or script returned non-zero." | tee -a "$REPORT_FILE"
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
  echo "$BLOCK_MARKER" | tee -a "$REPORT_FILE"
  echo "Reason: skillhub command unavailable after setup attempt." | tee -a "$REPORT_FILE"
  exit 21
fi

{
  echo "## CLI"
  command -v skillhub
  SKILLHUB_SKIP_SELF_UPGRADE=1 skillhub --version || skillhub --version || true
  echo
  echo "## Install requested skill"
} | tee -a "$REPORT_FILE"

if ! SKILLHUB_SKIP_SELF_UPGRADE=1 skillhub install "波动率策略" --dir "$SKILLS_DIR" --force; then
  echo "$BLOCK_MARKER" | tee -a "$REPORT_FILE"
  echo "Reason: skill install command returned non-zero." | tee -a "$REPORT_FILE"
  SKILLHUB_SKIP_SELF_UPGRADE=1 skillhub list --dir "$SKILLS_DIR" >> "$REPORT_FILE" 2>&1 || true
  exit 22
fi

{
  echo
  echo "## Installed list"
  SKILLHUB_SKIP_SELF_UPGRADE=1 skillhub list --dir "$SKILLS_DIR" || true
  echo
  echo "## Package preview"
  find "$SKILLS_DIR" -maxdepth 4 -type f | sed "s|$SKILLS_DIR/||" | head -200
} | tee -a "$REPORT_FILE"

tar -C "$SKILLS_DIR" -czf "$EXPORT_TGZ" .

{
  echo
  echo "## Export"
  echo "File: $EXPORT_TGZ"
  ls -lh "$EXPORT_TGZ"
  echo
  echo "SHA256:"
  shasum -a 256 "$EXPORT_TGZ" 2>/dev/null || sha256sum "$EXPORT_TGZ" 2>/dev/null || true
  echo
  echo "Completed: $(date '+%Y-%m-%d %H:%M:%S %z')"
  echo "$OK_MARKER"
} | tee -a "$REPORT_FILE"
```

## Expected repository output

Commit and push, when produced:

```text
skillhub_export/iwencai_skillhub_install_report.md
skillhub_export/iwencai_skillhub_skills_export.tar.gz
```

Also refresh normal visible status files with one marker:

```text
IWENCAI_SKILLHUB_EXPORT_OK_20260702
```

or

```text
IWENCAI_SKILLHUB_SETUP_BLOCKED_20260702
```
