#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


SAFETY_MODE = "PHASE_1_SIMULATION_ONLY"
STATE_FILE = "GPT_VISIBLE_REVIEW_STATE.json"
WORKFLOW_FILE = ".github/workflows/visible-review-scaffold.yml"
REVIEW_START = "<!-- visible-review-scaffold:start -->"
REVIEW_END = "<!-- visible-review-scaffold:end -->"
MAX_TEXT_BYTES = 60_000
MAX_ITEMS = 12

CORE_FILES = [
    "PROJECT_MEMORY.md",
    "TASK_QUEUE.md",
    "STATUS.md",
    "RUN_LOG.md",
    "WORKER_DASHBOARD.md",
    "GPT_VISIBLE_STATUS.md",
    "DECISION_REQUIRED.md",
]
SUMMARY_DIRS = ["REPORTS", "src", "tests"]
READY_STATUSES = {"pending", "queued", "todo"}
RUNNING_STATUSES = {"running"}
COMPLETED_STATUSES = {"completed"}

SENSITIVE_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{8,}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{8,}\b"),
    re.compile(
        r"(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|secret|password|authorization|credential)"
        r"(\s*[:=]\s*)(['\"]?)[^'\"\s]+"
    ),
]


@dataclass(frozen=True)
class QueueTask:
    task_id: str
    status: str
    task_type: str
    title: str
    request: str
    result: str
    safety: str

    def to_state(self) -> dict[str, str]:
        return {
            "id": self.task_id,
            "status": self.status,
            "type": self.task_type,
            "title": self.title,
            "request": summarize_inline(self.request, 220),
            "result": summarize_inline(self.result, 180),
            "safety": self.safety,
        }


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def now_text() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")


def redact(text: str) -> str:
    redacted = text
    redacted = SENSITIVE_PATTERNS[0].sub("sk-[REDACTED]", redacted)
    redacted = SENSITIVE_PATTERNS[1].sub("gh-[REDACTED]", redacted)
    redacted = SENSITIVE_PATTERNS[2].sub("AIza[REDACTED]", redacted)
    redacted = SENSITIVE_PATTERNS[3].sub(lambda m: f"{m.group(1)}{m.group(2)}[REDACTED]", redacted)
    return redacted


def read_text(path: Path, *, max_bytes: int = MAX_TEXT_BYTES) -> str:
    if not path.exists() or not path.is_file():
        return ""
    raw = path.read_bytes()[:max_bytes]
    return redact(raw.decode("utf-8", errors="replace"))


def summarize_inline(value: str, limit: int = 160) -> str:
    cleaned = re.sub(r"\s+", " ", redact(value)).strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3].rstrip() + "..."


def parse_queue_tasks(text: str) -> list[QueueTask]:
    tasks: list[QueueTask] = []
    current_id = ""
    fields: dict[str, str] = {}

    def flush() -> None:
        if not current_id:
            return
        tasks.append(
            QueueTask(
                task_id=current_id,
                status=fields.get("status", "").strip().lower(),
                task_type=fields.get("type", "").strip(),
                title=fields.get("title", "").strip(),
                request=fields.get("request", "").strip(),
                result=fields.get("result", "").strip(),
                safety=fields.get("safety", "").strip(),
            )
        )

    for line in text.splitlines():
        header = re.match(r"^###\s+([A-Za-z0-9_.-]+)\s*$", line)
        if header:
            flush()
            current_id = header.group(1)
            fields = {}
            continue
        item = re.match(r"^-\s*([A-Za-z][A-Za-z _-]*):\s*(.*)$", line)
        if current_id and item:
            key = item.group(1).strip().lower().replace(" ", "_").replace("-", "_")
            fields[key] = item.group(2).strip()
    flush()
    return tasks


def field_value(section: str, field: str) -> str:
    match = re.search(rf"(?mi)^-\s*{re.escape(field)}:\s*(.+)$", section)
    return summarize_inline(match.group(1), 220) if match else ""


def unresolved_decisions(text: str) -> list[str]:
    unresolved: list[str] = []

    def add(value: str) -> None:
        value = summarize_inline(value, 220)
        if value and value not in unresolved:
            unresolved.append(value)

    open_match = re.search(
        r"(?ms)^##\s+Open Decisions\s*(.*?)(?=^##\s+|\Z)",
        text,
    )
    if open_match:
        open_body = open_match.group(1)
        if not re.search(r"(?i)No current user action required", open_body):
            for line in re.findall(r"(?m)^-\s+(.+)$", open_body):
                if not re.search(r"(?i)\b(status|mode)\b", line):
                    add(line)

    for match in re.finditer(r"(?ms)^##\s+(Decision Required[^\n]*)\n(.*?)(?=^##\s+|\Z)", text):
        title, body = match.group(1), match.group(2)
        if re.search(r"(?mi)^-\s*Status:\s*resolved\s*$", body):
            continue
        add(field_value(body, "Item") or field_value(body, "Task") or title)

    for match in re.finditer(r"(?ms)^###\s+([^\n]+)\n(.*?)(?=^###\s+|^##\s+|\Z)", text):
        title, body = match.group(1), match.group(2)
        status = field_value(body, "Status").lower()
        if status == "resolved":
            continue
        if status in {"open", "pending", "decision_required"}:
            add(field_value(body, "Item") or field_value(body, "Task") or title)

    return unresolved


def latest_status_marker(text: str) -> str:
    matches = re.findall(r"(?m)^Status:\s*`?([^`\n]+)`?", text)
    return summarize_inline(matches[-1]) if matches else "UNKNOWN"


def latest_run_event(text: str) -> str:
    entries = re.findall(
        r"(?ms)^##\s+([^\n]+)\n\n-\s+Event:\s*([^\n]+)(.*?)(?=^##\s+|\Z)",
        text,
    )
    if not entries:
        return "none"
    timestamp, event, body = entries[-1]
    detail = field_value(body, "Detail") or field_value(body, "Summary")
    return summarize_inline(f"{timestamp} / {event} / {detail}", 240)


def markdown_headings(text: str, limit: int = 5) -> list[str]:
    headings = [
        summarize_inline(match.group(1), 120)
        for match in re.finditer(r"(?m)^#{1,3}\s+(.+)$", text)
    ]
    return headings[:limit]


def table_value(markdown: str, item: str) -> str:
    pattern = rf"(?m)^\|\s*{re.escape(item)}\s*\|\s*(.*?)\s*\|$"
    match = re.search(pattern, markdown)
    return summarize_inline(match.group(1), 180) if match else ""


def relative_file_list(root: Path, dirname: str, suffix: str | None = None) -> list[str]:
    directory = root / dirname
    if not directory.exists() or not directory.is_dir():
        return []
    files: list[Path] = []
    for path in directory.rglob("*"):
        if not path.is_file():
            continue
        if any(part.startswith(".") for part in path.relative_to(directory).parts):
            continue
        if suffix and path.suffix != suffix:
            continue
        files.append(path)
    return [path.relative_to(root).as_posix() for path in sorted(files)]


def summarize_reports(root: Path) -> dict[str, Any]:
    files = relative_file_list(root, "REPORTS")
    markdown_files = [root / rel for rel in files if rel.endswith(".md")]
    latest = ""
    headings: list[str] = []
    if markdown_files:
        latest_path = max(markdown_files, key=lambda path: path.stat().st_mtime)
        latest = latest_path.relative_to(root).as_posix()
        headings = markdown_headings(read_text(latest_path), 6)
    return {
        "count": len(files),
        "sample": files[:MAX_ITEMS],
        "latest_markdown": latest or "none",
        "latest_headings": headings,
    }


def summarize_python_tree(root: Path, dirname: str) -> dict[str, Any]:
    files = relative_file_list(root, dirname, ".py")
    return {
        "python_file_count": len(files),
        "sample": files[:MAX_ITEMS],
    }


def task_summary(task: QueueTask | None) -> str:
    if not task:
        return "None"
    label = task.title or task.request or task.task_type or "no title"
    result = f" | {task.result}" if task.result else ""
    return summarize_inline(f"{task.task_id} ({task.status}) - {label}{result}", 260)


def task_summary_from_state(task: dict[str, str] | None) -> str:
    if not task:
        return "None"
    label = task.get("title") or task.get("request") or task.get("type") or "no title"
    result = f" | {task.get('result')}" if task.get("result") else ""
    return summarize_inline(f"{task.get('id')} ({task.get('status')}) - {label}{result}", 260)


def file_presence(root: Path) -> dict[str, str]:
    required = CORE_FILES + SUMMARY_DIRS
    result: dict[str, str] = {}
    for rel in required:
        path = root / rel
        if path.is_dir():
            result[rel] = "present_dir"
        elif path.is_file():
            result[rel] = "present_file"
        else:
            result[rel] = "missing"
    workflow_path = root / WORKFLOW_FILE
    result[WORKFLOW_FILE] = "present_file" if workflow_path.is_file() else "not_installed"
    return result


def polling_state(root: Path, running: QueueTask | None, pending: QueueTask | None, decisions: list[str]) -> dict[str, Any]:
    path = root / "logs" / "worker_poll_state.json"
    payload: dict[str, Any] = {}
    if path.exists():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = {}
    mode = str(payload.get("mode", "")).upper()
    if mode not in {"ACTIVE", "WARM", "IDLE"}:
        if running or pending:
            mode = "ACTIVE"
        elif decisions:
            mode = "WARM"
        else:
            mode = "IDLE"
    if running or pending:
        mode = "ACTIVE"
    elif decisions and mode == "IDLE":
        mode = "WARM"
    interval = payload.get("interval_seconds")
    if not isinstance(interval, int):
        interval = {"ACTIVE": 30, "WARM": 60, "IDLE": 600}.get(mode, 600)
    return {
        "mode": mode,
        "interval_seconds": interval,
        "consecutive_idle_checks": int(payload.get("consecutive_idle_checks", 0) or 0),
        "reason": str(payload.get("reason", "not yet recorded")),
    }


def build_state(root: Path) -> dict[str, Any]:
    root = root.resolve()
    texts = {rel: read_text(root / rel) for rel in CORE_FILES}
    tasks = parse_queue_tasks(texts["TASK_QUEUE.md"])
    status_counts = Counter(task.status or "unknown" for task in tasks)
    running = next((task for task in tasks if task.status in RUNNING_STATUSES), None)
    pending = next((task for task in tasks if task.status in READY_STATUSES), None)
    completed = next((task for task in reversed(tasks) if task.status in COMPLETED_STATUSES), None)
    decisions = unresolved_decisions(texts["DECISION_REQUIRED.md"])
    presence = file_presence(root)
    missing = [rel for rel, value in presence.items() if value == "missing"]
    failure_reasons: list[str] = []
    if missing:
        failure_reasons.append("missing required repository paths: " + ", ".join(missing))
    if failure_reasons:
        state = "FAILED_WITH_REASON"
    elif running:
        state = "WORKER_BUSY"
    else:
        state = "SCAFFOLD_READY"

    if state == "FAILED_WITH_REASON":
        next_action = "Resolve the listed repository status issue, then rerun the visible review scaffold."
    elif state == "WORKER_BUSY":
        next_action = "Wait for the current worker task to finish; check DECISION_REQUIRED.md only if a new open item appears."
    elif pending:
        next_action = "Worker can execute the first pending repository-safe task on its next active cycle."
    else:
        next_action = "ChatGPT can review GPT_REVIEW.md and add the next safe simulation-only task to TASK_QUEUE.md."

    project_memory_headings = markdown_headings(texts["PROJECT_MEMORY.md"], 8)
    dashboard = texts["WORKER_DASHBOARD.md"]
    previous_visible = texts["GPT_VISIBLE_STATUS.md"]

    return {
        "generated_at": now_iso(),
        "state": state,
        "failure_reasons": failure_reasons,
        "safety_mode": SAFETY_MODE,
        "adaptive_polling": polling_state(root, running, pending, decisions),
        "current_task": running.to_state() if running else None,
        "first_pending_task": pending.to_state() if pending else None,
        "latest_completed_task": completed.to_state() if completed else None,
        "task_counts": dict(sorted(status_counts.items())),
        "decision_required": {
            "has_unresolved": bool(decisions),
            "items": decisions,
        },
        "latest_status_marker": latest_status_marker(texts["STATUS.md"]),
        "latest_run_event": latest_run_event(texts["RUN_LOG.md"]),
        "dashboard_state": table_value(dashboard, "Worker state") or "unknown",
        "dashboard_current_task": table_value(dashboard, "Current task") or "unknown",
        "previous_visible_status": latest_status_marker(previous_visible),
        "project_memory_headings": project_memory_headings,
        "reports": summarize_reports(root),
        "src_summary": summarize_python_tree(root, "src"),
        "tests_summary": summarize_python_tree(root, "tests"),
        "path_presence": presence,
        "next_action": next_action,
        "guarantees": [
            "repository-local summary only",
            "no network clients or external services",
            "no environment variable or secret-file reads",
            "no strategy code or data edits",
            "redacted status text in generated summaries",
        ],
    }


def build_visible_status(state: dict[str, Any]) -> str:
    decision = state["decision_required"]
    decision_text = "none"
    if decision["has_unresolved"]:
        decision_text = "; ".join(decision["items"])
    failure_text = "none"
    if state["failure_reasons"]:
        failure_text = "; ".join(state["failure_reasons"])
    return (
        "# GPT Visible Status\n\n"
        f"- Generated at: `{state['generated_at']}`\n"
        f"- Status: `{state['state']}`\n"
        f"- Visible scaffold: `{state['state']}`\n"
        f"- Worker mode: `{state['adaptive_polling']['mode']}`\n"
        f"- Current poll interval: `{state['adaptive_polling']['interval_seconds']}s`\n"
        f"- Consecutive idle checks: `{state['adaptive_polling']['consecutive_idle_checks']}`\n"
        f"- Polling reason: {state['adaptive_polling']['reason']}\n"
        f"- Safety mode: `{state['safety_mode']}`\n"
        f"- Current task: {task_summary_from_state(state['current_task'])}\n"
        f"- First pending task: {task_summary_from_state(state['first_pending_task'])}\n"
        f"- Latest completed task: {task_summary_from_state(state['latest_completed_task'])}\n"
        f"- Decision required: {decision_text}\n"
        f"- Failure reason: {failure_text}\n"
        f"- Latest status marker: `{state['latest_status_marker']}`\n"
        f"- Latest run event: {state['latest_run_event']}\n"
        f"- Dashboard state before scaffold refresh: `{state['dashboard_state']}`\n"
        f"- Reports reviewed: {state['reports']['count']} files; latest markdown `{state['reports']['latest_markdown']}`\n"
        f"- Source summary: {state['src_summary']['python_file_count']} Python files\n"
        f"- Test summary: {state['tests_summary']['python_file_count']} Python files\n"
        f"- Network calls: none from scaffold script\n"
        f"- Sensitive values: not read from env or secret files; generated text is redacted\n"
        f"- Next safe human-supervision action: {state['next_action']}\n\n"
        "## ChatGPT Supervision Contract\n\n"
        "- ChatGPT writes safe work into `TASK_QUEUE.md`.\n"
        "- The Mac mini worker executes repository-safe work and refreshes status files.\n"
        "- This review scaffold is status-only and stays inside `PHASE_1_SIMULATION_ONLY`.\n"
    )


def build_review_block(state: dict[str, Any]) -> str:
    reports = state["reports"]
    src = state["src_summary"]
    tests = state["tests_summary"]
    guarantees = "\n".join(f"- {item}" for item in state["guarantees"])
    report_headings = ", ".join(reports["latest_headings"]) if reports["latest_headings"] else "none"
    project_headings = ", ".join(state["project_memory_headings"]) if state["project_memory_headings"] else "none"
    failure = "; ".join(state["failure_reasons"]) if state["failure_reasons"] else "none"
    decision = "none"
    if state["decision_required"]["has_unresolved"]:
        decision = "; ".join(state["decision_required"]["items"])
    return (
        f"{REVIEW_START}\n"
        "## Visible Review Scaffold\n\n"
        f"- Generated at: `{state['generated_at']}`\n"
        f"- State: `{state['state']}`\n"
        f"- Safety mode: `{state['safety_mode']}`\n"
        f"- Worker mode: `{state['adaptive_polling']['mode']}`\n"
        f"- Current poll interval: `{state['adaptive_polling']['interval_seconds']}s`\n"
        f"- Consecutive idle checks: `{state['adaptive_polling']['consecutive_idle_checks']}`\n"
        f"- Current task: {task_summary_from_state(state['current_task'])}\n"
        f"- First pending task: {task_summary_from_state(state['first_pending_task'])}\n"
        f"- Latest completed task: {task_summary_from_state(state['latest_completed_task'])}\n"
        f"- Decision required: {decision}\n"
        f"- Failure reason: {failure}\n"
        f"- Latest status marker: `{state['latest_status_marker']}`\n"
        f"- Latest run event: {state['latest_run_event']}\n"
        f"- Previous dashboard state: `{state['dashboard_state']}`\n"
        f"- Previous visible status: `{state['previous_visible_status']}`\n"
        f"- Project memory headings reviewed: {project_headings}\n"
        f"- Reports summary: {reports['count']} files; latest markdown `{reports['latest_markdown']}`; headings: {report_headings}\n"
        f"- Source summary: {src['python_file_count']} Python files; sample: {', '.join(src['sample']) or 'none'}\n"
        f"- Test summary: {tests['python_file_count']} Python files; sample: {', '.join(tests['sample']) or 'none'}\n"
        f"- Next safe human-supervision action: {state['next_action']}\n\n"
        "## Scaffold Guarantees\n\n"
        f"{guarantees}\n"
        f"{REVIEW_END}\n"
    )


def refresh_review_file(root: Path, state: dict[str, Any]) -> None:
    path = root / "GPT_REVIEW.md"
    existing = read_text(path, max_bytes=500_000)
    block = build_review_block(state)
    if REVIEW_START in existing and REVIEW_END in existing:
        pattern = re.compile(
            rf"{re.escape(REVIEW_START)}.*?{re.escape(REVIEW_END)}",
            re.DOTALL,
        )
        updated = pattern.sub(block.strip(), existing)
    else:
        updated = existing.rstrip() + "\n\n" + block
    path.write_text(updated.rstrip() + "\n", encoding="utf-8")


def write_outputs(root: Path, state: dict[str, Any]) -> None:
    (root / "GPT_VISIBLE_STATUS.md").write_text(build_visible_status(state), encoding="utf-8")
    refresh_review_file(root, state)
    (root / STATE_FILE).write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def check_outputs(root: Path) -> tuple[bool, list[str]]:
    state = build_state(root)
    errors: list[str] = []
    visible = read_text(root / "GPT_VISIBLE_STATUS.md", max_bytes=200_000)
    review = read_text(root / "GPT_REVIEW.md", max_bytes=500_000)
    state_path = root / STATE_FILE

    if f"Visible scaffold: `{state['state']}`" not in visible:
        errors.append(f"GPT_VISIBLE_STATUS.md does not show Visible scaffold: `{state['state']}`")
    if f"Worker mode: `{state['adaptive_polling']['mode']}`" not in visible:
        errors.append(f"GPT_VISIBLE_STATUS.md does not show Worker mode: `{state['adaptive_polling']['mode']}`")
    if REVIEW_START not in review or REVIEW_END not in review:
        errors.append("GPT_REVIEW.md is missing visible review scaffold markers")
    if f"State: `{state['state']}`" not in review:
        errors.append(f"GPT_REVIEW.md does not show State: `{state['state']}`")
    if not state_path.is_file():
        errors.append(f"missing state file: {STATE_FILE}")
    else:
        try:
            saved = json.loads(state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{STATE_FILE} is invalid JSON: {exc}")
            saved = {}
        if saved.get("state") != state["state"]:
            errors.append(f"{STATE_FILE} does not match current state {state['state']}")

    script_text = read_text(Path(__file__), max_bytes=200_000)
    banned_imports = ["requests", "urllib", "http.client", "socket", "subprocess"]
    for banned in banned_imports:
        if re.search(rf"(?m)^\s*(import|from)\s+{re.escape(banned)}\b", script_text):
            errors.append(f"script imports network or process module: {banned}")

    return not errors, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refresh repository-only GPT visible review scaffold.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--check", action="store_true", help="Validate generated files without writing.")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if args.check:
        ok, errors = check_outputs(root)
        if ok:
            if not args.quiet:
                print("PASS")
            return 0
        if not args.quiet:
            print("FAIL")
            for error in errors:
                print(f"- {error}")
        return 1

    state = build_state(root)
    write_outputs(root, state)
    if not args.quiet:
        print(f"refreshed visible review scaffold: {state['state']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
