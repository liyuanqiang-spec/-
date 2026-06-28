#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


SAFETY_MODE = "PHASE_1_SIMULATION_ONLY"
MARKER = "LOCAL_REVIEW_TRIGGER_DRY_RUN_READY"
INPUT_FILE = "GPT_LOCAL_REVIEW_INPUT.md"
REVIEW_START = "<!-- local-review-trigger-dry-run:start -->"
REVIEW_END = "<!-- local-review-trigger-dry-run:end -->"
MAX_TEXT_BYTES = 80_000
MAX_ITEMS = 6

CORE_INPUT_FILES = [
    "TASK_QUEUE.md",
    "STATUS.md",
    "RUN_LOG.md",
    "WORKER_DASHBOARD.md",
    "GPT_VISIBLE_STATUS.md",
    "DECISION_REQUIRED.md",
    "GPT_REVIEW_PACKET.md",
    "REPORTS/model_review_packet.md",
]

SENSITIVE_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{8,}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{8,}\b"),
    re.compile(
        r"(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|secret|password|authorization|credential)"
        r"(\s*[:=]\s*)(['\"]?)[^'\"\s]+"
    ),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._-]{8,}\b"),
    re.compile(r"/Users/[^\s`'\"),]+"),
    re.compile(r"/private/[^\s`'\"),]+"),
]


@dataclass(frozen=True)
class QueueTask:
    task_id: str
    status: str
    task_type: str
    title: str
    result: str
    safety: str


@dataclass(frozen=True)
class ReviewContext:
    generated_at: str
    trigger_message: str
    worker_state: str
    visible_scaffold: str
    worker_mode: str
    current_task: str
    latest_completed_task: str
    decision_required: str
    latest_status_marker: str
    latest_run_events: list[str]
    input_files: list[str]
    report_summary: list[str]


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def redact(text: str) -> str:
    redacted = text
    redacted = SENSITIVE_PATTERNS[0].sub("sk-[REDACTED]", redacted)
    redacted = SENSITIVE_PATTERNS[1].sub("gh-[REDACTED]", redacted)
    redacted = SENSITIVE_PATTERNS[2].sub("AIza[REDACTED]", redacted)
    redacted = SENSITIVE_PATTERNS[3].sub(lambda m: f"{m.group(1)}{m.group(2)}[REDACTED]", redacted)
    redacted = SENSITIVE_PATTERNS[4].sub("Bearer [REDACTED]", redacted)
    redacted = SENSITIVE_PATTERNS[5].sub("[LOCAL_PATH]", redacted)
    redacted = SENSITIVE_PATTERNS[6].sub("[LOCAL_PATH]", redacted)
    return redacted


def read_text(path: Path, *, max_bytes: int = MAX_TEXT_BYTES) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return redact(path.read_bytes()[:max_bytes].decode("utf-8", errors="replace"))


def one_line(text: str, limit: int = 220) -> str:
    value = re.sub(r"\s+", " ", redact(text)).strip()
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def visible_value(text: str, field: str) -> str:
    match = re.search(rf"(?m)^-\s*{re.escape(field)}:\s*(.+)$", text)
    if not match:
        return ""
    return one_line(match.group(1).strip().strip("`"))


def table_value(text: str, item: str) -> str:
    pattern = rf"(?m)^\|\s*{re.escape(item)}\s*\|\s*(.*?)\s*\|$"
    match = re.search(pattern, text)
    return one_line(match.group(1)) if match else ""


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


def task_summary(task: QueueTask | None) -> str:
    if task is None:
        return "none"
    label = task.title or task.task_type or "no title"
    result = f" | {task.result}" if task.result else ""
    return one_line(f"{task.task_id} ({task.status}) - {label}{result}", 260)


def latest_status_marker(status_text: str) -> str:
    matches = re.findall(r"(?m)^Status:\s*`?([^`\n]+)`?", status_text)
    return one_line(matches[-1]) if matches else "UNKNOWN"


def latest_run_events(run_log_text: str, limit: int = 5) -> list[str]:
    entries = re.findall(
        r"(?ms)^##\s+([^\n]+)\n\n-\s+Event:\s*([^\n]+)(.*?)(?=^##\s+|\Z)",
        run_log_text,
    )
    result: list[str] = []
    for timestamp, event, body in entries[-limit:]:
        detail_match = re.search(r"(?mi)^-\s*Detail:\s*(.+)$", body)
        detail = detail_match.group(1).strip() if detail_match else ""
        result.append(one_line(f"{timestamp} / {event} / {detail}", 260))
    return result or ["none"]


def bullet_lines(text: str, limit: int = MAX_ITEMS) -> list[str]:
    values: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^\s*[-*]\s+(.+)$", line)
        if match:
            values.append(one_line(match.group(1), 240))
        if len(values) >= limit:
            break
    return values


def section_body(text: str, heading: str) -> str:
    pattern = rf"(?ms)^##\s+{re.escape(heading)}\s*\n(?P<body>.*?)(?=^##\s+|\Z)"
    match = re.search(pattern, text)
    return match.group("body").strip() if match else ""


def report_summary(root: Path) -> list[str]:
    packet_text = read_text(root / "GPT_REVIEW_PACKET.md")
    if packet_text:
        values = bullet_lines(section_body(packet_text, "Current State"), 3)
        values.extend(bullet_lines(section_body(packet_text, "Latest Report Summary"), 3))
        if values:
            return values[:MAX_ITEMS]
    visible = read_text(root / "GPT_VISIBLE_STATUS.md")
    values = [
        f"Status: {visible_value(visible, 'Status') or 'UNKNOWN'}",
        f"Latest completed task: {visible_value(visible, 'Latest completed task') or 'none'}",
    ]
    return values


def present_input_files(root: Path) -> list[str]:
    return [rel for rel in CORE_INPUT_FILES if (root / rel).is_file()]


def build_context(root: Path, trigger_message: str) -> ReviewContext:
    queue_text = read_text(root / "TASK_QUEUE.md")
    status_text = read_text(root / "STATUS.md")
    run_log_text = read_text(root / "RUN_LOG.md")
    visible_text = read_text(root / "GPT_VISIBLE_STATUS.md")
    dashboard_text = read_text(root / "WORKER_DASHBOARD.md")
    tasks = parse_queue_tasks(queue_text)
    current = next((task for task in tasks if task.status in {"running", "pending", "queued", "todo"}), None)
    latest_completed = next((task for task in reversed(tasks) if task.status == "completed"), None)
    return ReviewContext(
        generated_at=now_iso(),
        trigger_message=one_line(trigger_message or "manual local dry run", 180),
        worker_state=visible_value(visible_text, "Status") or table_value(dashboard_text, "Worker state") or "UNKNOWN",
        visible_scaffold=visible_value(visible_text, "Visible scaffold")
        or table_value(dashboard_text, "Visible scaffold")
        or "UNKNOWN",
        worker_mode=visible_value(visible_text, "Worker mode") or table_value(dashboard_text, "Worker mode") or "UNKNOWN",
        current_task=task_summary(current),
        latest_completed_task=task_summary(latest_completed),
        decision_required=visible_value(visible_text, "Decision required")
        or table_value(dashboard_text, "Decision required")
        or "none",
        latest_status_marker=latest_status_marker(status_text),
        latest_run_events=latest_run_events(run_log_text),
        input_files=present_input_files(root),
        report_summary=report_summary(root),
    )


def markdown_list(items: list[str]) -> str:
    return "\n".join(f"- {one_line(item, 260)}" for item in items)


def build_review_input(context: ReviewContext) -> str:
    input_files = markdown_list(context.input_files)
    report = markdown_list(context.report_summary)
    run_events = markdown_list(context.latest_run_events)
    return (
        "# GPT Local Review Input\n\n"
        f"- Marker: `{MARKER}`\n"
        f"- Generated at: `{context.generated_at}`\n"
        f"- Safety mode: `{SAFETY_MODE}`\n"
        "- Scope: repository-local deterministic dry run only.\n"
        "- Network calls: none.\n"
        "- Task creation: disabled; this file does not append or propose queue mutations.\n"
        f"- Trigger: {context.trigger_message}\n\n"
        "## Compact Worker State\n\n"
        f"- Worker state: `{context.worker_state}`\n"
        f"- Visible scaffold: `{context.visible_scaffold}`\n"
        f"- Worker mode: `{context.worker_mode}`\n"
        f"- Current task: {context.current_task}\n"
        f"- Latest completed task: {context.latest_completed_task}\n"
        f"- Decision required: {context.decision_required}\n"
        f"- Latest status marker: `{context.latest_status_marker}`\n\n"
        "## Recent Run Events\n\n"
        f"{run_events}\n\n"
        "## Review Packet Summary\n\n"
        f"{report}\n\n"
        "## Inputs Used\n\n"
        f"{input_files}\n\n"
        "## Boundaries\n\n"
        "- No broker, exchange, trading-account, order, fund, credential, or external-service access.\n"
        "- No raw market data dump and no strategy/data file edits.\n"
        "- Generated text is redacted for credential-like values and private absolute paths.\n"
    )


def build_review_block(context: ReviewContext) -> str:
    return (
        f"{REVIEW_START}\n"
        "## Local Review Trigger Dry Run\n\n"
        f"- Marker: `{MARKER}`\n"
        f"- Generated at: `{context.generated_at}`\n"
        f"- Input file: `{INPUT_FILE}`\n"
        f"- Safety mode: `{SAFETY_MODE}`\n"
        "- Default state: disabled unless `LOCAL_REVIEW_TRIGGER_DRY_RUN_ENABLED=1` is set for the worker.\n"
        "- Network calls: none.\n"
        "- Task append: none.\n"
        f"- Trigger: {context.trigger_message}\n"
        f"- Worker state: `{context.worker_state}`\n"
        f"- Latest completed task: {context.latest_completed_task}\n"
        f"- Decision required: {context.decision_required}\n"
        f"{REVIEW_END}\n"
    )


def refresh_review_file(root: Path, context: ReviewContext) -> None:
    path = root / "GPT_REVIEW.md"
    existing = read_text(path, max_bytes=500_000)
    block = build_review_block(context)
    if REVIEW_START in existing and REVIEW_END in existing:
        pattern = re.compile(rf"{re.escape(REVIEW_START)}.*?{re.escape(REVIEW_END)}", re.DOTALL)
        updated = pattern.sub(block.strip(), existing)
    else:
        updated = existing.rstrip() + "\n\n" + block
    path.write_text(updated.rstrip() + "\n", encoding="utf-8")


def load_refresh_visible_status(root: Path) -> Any:
    candidates = [
        root / "scripts" / "refresh_visible_status.py",
        Path(__file__).resolve().with_name("refresh_visible_status.py"),
    ]
    for candidate in candidates:
        if not candidate.is_file():
            continue
        spec = importlib.util.spec_from_file_location("refresh_visible_status_for_local_review", candidate)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    raise RuntimeError("refresh_visible_status.py is not available")


def write_outputs(root: Path, context: ReviewContext) -> None:
    (root / INPUT_FILE).write_text(build_review_input(context), encoding="utf-8")
    refresh_review_file(root, context)
    refresh_module = load_refresh_visible_status(root)
    state = refresh_module.build_state(root)
    refresh_module.write_outputs(root, state)


def check_outputs(root: Path) -> tuple[bool, list[str]]:
    errors: list[str] = []
    input_text = read_text(root / INPUT_FILE, max_bytes=500_000)
    review_text = read_text(root / "GPT_REVIEW.md", max_bytes=500_000)
    visible_text = read_text(root / "GPT_VISIBLE_STATUS.md", max_bytes=500_000)
    state_path = root / ".gpt_state.json"

    if MARKER not in input_text:
        errors.append(f"{INPUT_FILE} missing marker {MARKER}")
    if REVIEW_START not in review_text or REVIEW_END not in review_text or MARKER not in review_text:
        errors.append("GPT_REVIEW.md missing local review dry-run marker block")
    if f"Local review trigger: `{MARKER}`" not in visible_text:
        errors.append("GPT_VISIBLE_STATUS.md does not expose local review dry-run readiness")
    if not state_path.is_file():
        errors.append("missing .gpt_state.json")
    else:
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            state = {}
            errors.append(f".gpt_state.json is invalid JSON: {exc}")
        if state.get("local_review_trigger", {}).get("state") != MARKER:
            errors.append(".gpt_state.json does not record local review dry-run readiness")

    for rel, text in (
        (INPUT_FILE, input_text),
        ("GPT_REVIEW.md", review_text),
        ("GPT_VISIBLE_STATUS.md", visible_text),
    ):
        if re.search(r"/Users/|/private/|sk-[A-Za-z0-9_-]{8,}|gh[pousr]_[A-Za-z0-9_]{8,}", text):
            errors.append(f"{rel} contains unredacted private path or credential-like token")
    return not errors, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a repository-local post-push review trigger dry run.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--trigger-message", default="manual local dry run")
    parser.add_argument("--check", action="store_true")
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

    context = build_context(root, args.trigger_message)
    write_outputs(root, context)
    if not args.quiet:
        print(f"local review trigger dry run ready: {INPUT_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
