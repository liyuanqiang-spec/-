#!/usr/bin/env python3
"""Cloud GPT supervisor for the repository-led Codex workflow.

This script is intended to run from GitHub Actions. It reads repository status
files, asks the OpenAI Responses API for a structured supervision decision, and
writes review/status artifacts back into the repository. It only appends one
safe repository-only task when the queue is idle.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

STATUS_PATHS = [
    "TASK_QUEUE.md",
    "STATUS.md",
    "RUN_LOG.md",
    "WORKER_DASHBOARD.md",
    "DECISION_REQUIRED.md",
    "GPT_REVIEW.md",
    "GPT_VISIBLE_STATUS.md",
    "RELIABILITY_RUNBOOK.md",
    "QUANT_SYSTEM_TARGETS.md",
    "GPT_REVIEW_PACKET.md",
    "GPT_LOCAL_REVIEW_INPUT.md",
]

REPORTS_DIR = ROOT / "REPORTS"

HARD_STOP_PATTERNS = [
    r"real\s+trading",
    r"live\s+trading",
    r"broker",
    r"trading\s+account",
    r"place\s+orders?",
    r"cancel\s+orders?",
    r"move\s+funds?",
    r"wire\s+transfer",
    r"withdraw",
    r"deposit",
    r"password",
    r"credential",
    r"secret",
    r"api\s*key",
    r"token",
    r"delete\s+raw",
    r"delete\s+original",
    r"danger-full-access",
    r"dangerous\s+permissions?",
]

MAX_FILE_CHARS = 8_000
MAX_CONTEXT_CHARS = 55_000


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def rel(path: str) -> Path:
    return ROOT / path


def read_text(path: str, max_chars: int = MAX_FILE_CHARS) -> str:
    p = rel(path)
    if not p.exists():
        return f"[missing: {path}]"
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:  # pragma: no cover - defensive in CI
        return f"[unreadable: {path}: {exc}]"
    if len(text) > max_chars:
        return text[:max_chars] + f"\n\n[truncated {len(text) - max_chars} chars]"
    return text


def write_text_if_changed(path: str, content: str) -> bool:
    p = rel(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    old = p.read_text(encoding="utf-8", errors="replace") if p.exists() else None
    if old == content:
        return False
    p.write_text(content, encoding="utf-8")
    return True


def extract_output_text(response: dict[str, Any]) -> str:
    if isinstance(response.get("output_text"), str):
        return response["output_text"]
    chunks: list[str] = []
    for item in response.get("output", []) or []:
        for part in item.get("content", []) or []:
            if isinstance(part, dict):
                if isinstance(part.get("text"), str):
                    chunks.append(part["text"])
                elif isinstance(part.get("output_text"), str):
                    chunks.append(part["output_text"])
    return "\n".join(chunks).strip()


def parse_json_object(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, flags=re.S)
    if not match:
        raise ValueError("model response did not contain a JSON object")
    return json.loads(match.group(0))


def parse_task_queue() -> dict[str, Any]:
    text = read_text("TASK_QUEUE.md", max_chars=200_000)
    sections = re.findall(
        r"^###\s+(TASK-[A-Za-z0-9-]+)(.*?)(?=^###\s+TASK-|\Z)",
        text,
        flags=re.M | re.S,
    )
    tasks: list[dict[str, str]] = []
    for task_id, body in sections:
        status_match = re.search(r"^- Status:\s*([^\n]+)", body, flags=re.M)
        title_match = re.search(r"^- Title:\s*([^\n]+)", body, flags=re.M)
        safety_match = re.search(r"^- Safety:\s*([^\n]+)", body, flags=re.M)
        tasks.append(
            {
                "id": task_id.strip(),
                "status": (status_match.group(1).strip() if status_match else "unknown"),
                "title": (title_match.group(1).strip() if title_match else ""),
                "safety": (safety_match.group(1).strip() if safety_match else ""),
            }
        )
    first_pending = next((t for t in tasks if t["status"].lower() == "pending"), None)
    running = next((t for t in tasks if t["status"].lower() in {"running", "in_progress"}), None)
    completed = [t for t in tasks if t["status"].lower() == "completed"]
    latest_completed = completed[-1] if completed else None
    return {
        "tasks": tasks,
        "first_pending": first_pending,
        "running": running,
        "latest_completed": latest_completed,
    }


def unresolved_decision() -> str:
    text = read_text("DECISION_REQUIRED.md", max_chars=40_000)
    if "No current user action required" in text:
        return "none"
    if "## Open Decisions" in text:
        after = text.split("## Open Decisions", 1)[1]
        before_resolved = after.split("## Resolved Decisions", 1)[0].strip()
        return before_resolved or "open decision present"
    return "unknown"


def collect_context(queue: dict[str, Any]) -> str:
    blocks: list[str] = []
    meta = {
        "generated_at": now_iso(),
        "source": "github_actions_openai_api",
        "first_pending": queue.get("first_pending"),
        "running": queue.get("running"),
        "latest_completed": queue.get("latest_completed"),
        "unresolved_decision": unresolved_decision(),
    }
    blocks.append("## Parsed machine state\n" + json.dumps(meta, ensure_ascii=False, indent=2))
    for path in STATUS_PATHS:
        blocks.append(f"\n\n## FILE: {path}\n" + read_text(path))
    if REPORTS_DIR.exists():
        for report in sorted(REPORTS_DIR.glob("*.md"))[-12:]:
            rel_path = report.relative_to(ROOT).as_posix()
            blocks.append(f"\n\n## FILE: {rel_path}\n" + read_text(rel_path))
    context = "".join(blocks)
    if len(context) > MAX_CONTEXT_CHARS:
        context = context[:MAX_CONTEXT_CHARS] + f"\n\n[context truncated to {MAX_CONTEXT_CHARS} chars]"
    return context


def call_openai(context: str) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY missing")
    model = os.getenv("OPENAI_MODEL", "").strip() or "gpt-5.5"
    instructions = """
You are the owner's cloud supervisor for a GitHub-led Codex workflow.
Return only a strict JSON object. No markdown fences.

Required JSON keys:
- summary: short Chinese summary of the worker state.
- worker_state: one of IDLE, RUNNING, PENDING, BLOCKED, UNKNOWN.
- latest_completed_task: string.
- unresolved_blocker: string, use none if no blocker.
- next_action: short Chinese next action.
- safety_assessment: short Chinese safety check.
- should_append_task: boolean.
- append_task_markdown: string. Empty unless should_append_task is true.

Task append policy:
- If a task is running, do not append.
- If any pending task exists, do not append.
- If unresolved blocker exists, do not append unless the append task is a narrower safe repository-only status/simulation remediation task.
- Append at most one task.
- Any appended task must be repository-only and must include these lines:
  - Status: pending
  - Safety: repository_status_only
- Keep PHASE_1_SIMULATION_ONLY.

Hard stops:
- Never suggest connecting real trading accounts.
- Never suggest placing/canceling orders or moving funds.
- Never ask to read, print, log, commit, or expose keys/tokens/passwords/secrets.
- Never suggest deleting original/raw data.
- Never use dangerous permissions.

Priority:
1. Get the cloud GitHub Actions + OpenAI/Codex loop working end-to-end.
2. Prefer existing platform/plugin capabilities over custom worker hooks.
3. Keep tasks small and directly executable.
""".strip()
    payload = {
        "model": model,
        "instructions": instructions,
        "input": context,
        "max_output_tokens": 2200,
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")[:2000]
        raise RuntimeError(f"OpenAI API HTTP {exc.code}: {details}") from exc
    data = json.loads(body)
    text = extract_output_text(data)
    if not text:
        raise RuntimeError("OpenAI API returned no output text")
    parsed = parse_json_object(text)
    parsed["_raw_response_text"] = text
    parsed["_model"] = model
    return parsed


def hard_stop_hit(markdown: str) -> str | None:
    lower = markdown.lower()
    for pattern in HARD_STOP_PATTERNS:
        if re.search(pattern, lower):
            return pattern
    return None


def ensure_task_markdown(markdown: str) -> str:
    text = markdown.strip()
    if not text:
        return ""
    if not re.search(r"^###\s+TASK-", text, flags=re.M):
        task_id = "TASK-AUTO-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d%H%M%S")
        text = f"### {task_id}\n" + text
    if "- Status: pending" not in text:
        text += "\n- Status: pending"
    if "- Safety: repository_status_only" not in text:
        text += "\n- Safety: repository_status_only"
    if "- Created:" not in text:
        text += "\n- Created: " + dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    return text.strip() + "\n"


def append_task_if_safe(review: dict[str, Any], queue: dict[str, Any]) -> tuple[bool, str]:
    if queue.get("running"):
        return False, "running task exists"
    if queue.get("first_pending"):
        return False, "pending task exists"
    if not bool(review.get("should_append_task")):
        return False, "model did not request append"
    markdown = ensure_task_markdown(str(review.get("append_task_markdown") or ""))
    if not markdown.strip():
        return False, "append markdown empty"
    hit = hard_stop_hit(markdown)
    if hit:
        return False, f"blocked by hard-stop pattern: {hit}"
    if "repository_status_only" not in markdown:
        return False, "missing repository_status_only safety"
    queue_path = rel("TASK_QUEUE.md")
    old = queue_path.read_text(encoding="utf-8", errors="replace") if queue_path.exists() else "# TASK_QUEUE.md\n\n## Tasks\n"
    task_id_match = re.search(r"^###\s+(TASK-[A-Za-z0-9-]+)", markdown, flags=re.M)
    if task_id_match and re.search(rf"^###\s+{re.escape(task_id_match.group(1))}\b", old, flags=re.M):
        suffix = dt.datetime.now(dt.timezone.utc).strftime("%H%M%S")
        markdown = re.sub(
            r"^###\s+(TASK-[A-Za-z0-9-]+)",
            lambda m: f"### {m.group(1)}-{suffix}",
            markdown,
            count=1,
            flags=re.M,
        )
    new = old.rstrip() + "\n\n" + markdown
    queue_path.write_text(new, encoding="utf-8")
    return True, "task appended"


def render_review(review: dict[str, Any], appended: bool, append_reason: str, queue: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# GPT Review",
            "",
            "## Cloud supervisor",
            f"- Generated at: `{now_iso()}`",
            "- Source: `github_actions_openai_api`",
            "- OPENAI_API_KEY present: `True`",
            f"- Model: `{review.get('_model', os.getenv('OPENAI_MODEL', '') or 'gpt-5.5')}`",
            f"- Worker state: `{review.get('worker_state', 'UNKNOWN')}`",
            f"- Latest completed task: {review.get('latest_completed_task', 'unknown')}",
            f"- Unresolved blocker: {review.get('unresolved_blocker', 'unknown')}",
            f"- First pending before review: {queue.get('first_pending') or 'none'}",
            f"- Running before review: {queue.get('running') or 'none'}",
            f"- Appended task: `{appended}` ({append_reason})",
            "",
            "## Summary",
            str(review.get("summary", "")),
            "",
            "## Safety assessment",
            str(review.get("safety_assessment", "")),
            "",
            "## Next action",
            str(review.get("next_action", "")),
            "",
        ]
    )


def render_visible_status(review: dict[str, Any], appended: bool, append_reason: str, queue: dict[str, Any]) -> str:
    next_action = str(review.get("next_action", ""))
    return "\n".join(
        [
            "# GPT Visible Status",
            "",
            f"- Generated at: `{now_iso()}`",
            f"- Status: `{review.get('worker_state', 'UNKNOWN')}`",
            "- Visible scaffold: `SCAFFOLD_READY`",
            "- Cloud supervisor: `GITHUB_ACTIONS_OPENAI_API_READY`",
            "- Codex runner: `CODEX_GITHUB_ACTION_INSTALLED`",
            "- Safety mode: `PHASE_1_SIMULATION_ONLY`",
            f"- Current task: {queue.get('running') or 'none'}",
            f"- First pending task: {queue.get('first_pending') or 'none'}",
            f"- Latest completed task: {queue.get('latest_completed') or 'unknown'}",
            f"- Decision required: {review.get('unresolved_blocker', 'unknown')}",
            f"- Appended task: `{appended}` ({append_reason})",
            f"- Next action: {next_action}",
            "",
            "## Cloud automation contract",
            "",
            "- `GPT Supervisor` reads repository status files and writes review/status outputs.",
            "- `Codex Task Runner` executes only the first safe pending repository task.",
            "- Mac mini is no longer required for cloud repository supervision.",
        ]
    )


def main() -> int:
    if not os.getenv("OPENAI_API_KEY", "").strip():
        print("OPENAI_API_KEY present: False")
        return 0
    print("OPENAI_API_KEY present: True")
    queue = parse_task_queue()
    context = collect_context(queue)
    try:
        review = call_openai(context)
        appended, append_reason = append_task_if_safe(review, queue)
    except Exception as exc:  # keep workflow diagnostic but do not expose secrets
        review = {
            "summary": f"云端 supervisor 运行失败：{exc}",
            "worker_state": "UNKNOWN",
            "latest_completed_task": str((queue.get("latest_completed") or {}).get("id", "unknown")),
            "unresolved_blocker": "cloud supervisor error",
            "next_action": "检查 GitHub Actions 日志和 OPENAI_MODEL / OPENAI_API_KEY 设置。",
            "safety_assessment": "未执行任务追加。",
            "should_append_task": False,
            "append_task_markdown": "",
            "_model": os.getenv("OPENAI_MODEL", "") or "gpt-5.5",
        }
        appended, append_reason = False, f"supervisor error: {exc}"
    state = {
        "generated_at": now_iso(),
        "source": "github_actions_openai_api",
        "worker_state": review.get("worker_state", "UNKNOWN"),
        "latest_completed_task": review.get("latest_completed_task"),
        "unresolved_blocker": review.get("unresolved_blocker"),
        "first_pending_before_review": queue.get("first_pending"),
        "running_before_review": queue.get("running"),
        "appended_task": appended,
        "append_reason": append_reason,
        "safety_mode": "PHASE_1_SIMULATION_ONLY",
    }
    write_text_if_changed("GPT_REVIEW.md", render_review(review, appended, append_reason, queue))
    write_text_if_changed("GPT_VISIBLE_STATUS.md", render_visible_status(review, appended, append_reason, queue))
    write_text_if_changed(".gpt_state.json", json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(state, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
