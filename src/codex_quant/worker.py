from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from . import run_pipeline
from .config import DECISION_REQUIRED, PROJECT_ROOT, RUN_LOG, STATUS_FILE, TASK_QUEUE
from .dashboard import update_dashboard


SAFE_TASK_TYPES = {"pipeline", "report", "test", "status_check"}
READY_STATUSES = {"pending", "queued"}
BLOCKED_KEYWORDS = {
    "真实交易": "real trading is blocked",
    "真实下单": "real order placement is blocked",
    "实盘下单": "real order placement is blocked",
    "撤单": "broker-side cancel requires confirmation",
    "资金划转": "fund transfer is blocked",
    "保证金划转": "margin movement is blocked",
    "券商权限": "broker permission change requires confirmation",
    "删除原始数据": "destructive raw-data deletion is blocked",
    "泄露密钥": "secret exposure is blocked",
    "密钥": "secret handling requires confirmation",
    "danger-full-access": "danger-full-access requires confirmation",
    "系统级修改": "system-level change requires confirmation",
    "大额付费": "large paid call requires confirmation",
    "real trading": "real trading is blocked",
    "real order": "real order placement is blocked",
    "fund transfer": "fund transfer is blocked",
    "delete raw data": "destructive raw-data deletion is blocked",
    "secret": "secret handling requires confirmation",
    "system-level": "system-level change requires confirmation",
}


@dataclass(frozen=True)
class QueueTask:
    task_id: str
    status: str
    task_type: str
    request: str


@dataclass(frozen=True)
class TaskResult:
    status: str
    summary: str


def now_text() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def parse_task_queue(text: str) -> list[QueueTask]:
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
                task_type=fields.get("type", "").strip().lower(),
                request=fields.get("request", "").strip(),
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


def blocked_reason(task: QueueTask) -> str | None:
    text = f"{task.task_type} {task.request}".lower()
    for keyword, reason in BLOCKED_KEYWORDS.items():
        if keyword.lower() in text:
            return reason
    if task.task_type not in SAFE_TASK_TYPES:
        return f"unsupported task type: {task.task_type or 'empty'}"
    return None


def append_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def append_run_log(event: str, task_id: str, summary: str) -> None:
    append_markdown(
        RUN_LOG,
        [
            "",
            f"## {now_text()}",
            "",
            f"- Event: {event}",
            f"- Task: {task_id}",
            f"- Summary: {summary}",
        ],
    )


def append_status_update(task_id: str, summary: str) -> None:
    append_markdown(
        STATUS_FILE,
        [
            "",
            f"## Worker Update {now_text()}",
            "",
            "Status: `WORKER_RAN_SAFE_TASK`",
            "",
            f"- Task: {task_id}",
            f"- Result: {summary}",
            "- Safety mode: `SIMULATION_ONLY`",
        ],
    )


def append_decision(task: QueueTask, reason: str) -> None:
    append_markdown(
        DECISION_REQUIRED,
        [
            "",
            f"## Decision Required {now_text()}",
            "",
            f"- Task: {task.task_id}",
            f"- Type: {task.task_type or 'empty'}",
            f"- Request: {task.request or 'empty'}",
            f"- Block reason: {reason}",
            "- Current action: stopped before execution",
            "- A 推荐: keep `SIMULATION_ONLY` and rewrite the task as data/backtest/report work",
            "- B: explicitly approve the blocked action in writing",
            "- C: cancel this task",
        ],
    )


def clean_value(value: str) -> str:
    return value.replace("\n", " ").replace("|", "/")[:320]


def update_task_block(text: str, task_id: str, updates: dict[str, str]) -> str:
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if re.match(rf"^###\s+{re.escape(task_id)}\s*$", line):
            start = index
            break
    if start is None:
        return text

    end = len(lines)
    for index in range(start + 1, len(lines)):
        if re.match(r"^###\s+[A-Za-z0-9_.-]+\s*$", lines[index]):
            end = index
            break

    existing: dict[str, int] = {}
    for index in range(start + 1, end):
        item = re.match(r"^-\s*([A-Za-z][A-Za-z _-]*):", lines[index])
        if item:
            key = item.group(1).strip().lower().replace(" ", "_").replace("-", "_")
            existing[key] = index

    insert_at = end
    for raw_key, raw_value in updates.items():
        key = raw_key.strip().lower().replace(" ", "_").replace("-", "_")
        label = raw_key.strip()
        value = clean_value(raw_value)
        if key in existing:
            lines[existing[key]] = f"- {label}: {value}"
        else:
            lines.insert(insert_at, f"- {label}: {value}")
            insert_at += 1
    return "\n".join(lines) + "\n"


def execute_task(task: QueueTask) -> TaskResult:
    reason = blocked_reason(task)
    if reason:
        append_decision(task, reason)
        return TaskResult("decision_required", reason)

    if task.task_type in {"pipeline", "report"}:
        result = run_pipeline.run()
        return TaskResult(
            "completed",
            f"pipeline completed: contracts={result['contracts']}, candidates={result['candidates']}, report={result['report']}",
        )

    if task.task_type == "test":
        completed = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "tests"],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            timeout=180,
            check=False,
        )
        output = (completed.stdout + "\n" + completed.stderr).strip().splitlines()
        tail = " ".join(output[-4:]) if output else "no output"
        if completed.returncode == 0:
            return TaskResult("completed", f"tests passed: {tail}")
        return TaskResult("failed", f"tests failed: {tail}")

    if task.task_type == "status_check":
        return TaskResult("completed", "status files readable; worker is alive")

    append_decision(task, "unreachable unsupported task")
    return TaskResult("decision_required", "unreachable unsupported task")


def process_once() -> int:
    if not TASK_QUEUE.exists():
        return 0

    text = TASK_QUEUE.read_text(encoding="utf-8")
    tasks = parse_task_queue(text)
    ready = [task for task in tasks if task.status in READY_STATUSES]
    if not ready:
        return 0

    processed = 0
    for task in ready:
        append_run_log("started", task.task_id, task.request or task.task_type)
        text = TASK_QUEUE.read_text(encoding="utf-8")
        text = update_task_block(text, task.task_id, {"Status": "running", "Last update": now_text()})
        TASK_QUEUE.write_text(text, encoding="utf-8")

        try:
            result = execute_task(task)
        except Exception as exc:  # noqa: BLE001 - worker must log failures instead of hiding them.
            result = TaskResult("failed", f"{type(exc).__name__}: {exc}")

        text = TASK_QUEUE.read_text(encoding="utf-8")
        text = update_task_block(
            text,
            task.task_id,
            {"Status": result.status, "Last update": now_text(), "Result": result.summary},
        )
        TASK_QUEUE.write_text(text, encoding="utf-8")
        append_run_log(result.status, task.task_id, result.summary)
        if result.status == "completed":
            append_status_update(task.task_id, result.summary)
        processed += 1
    update_dashboard()
    return processed


def main() -> int:
    parser = argparse.ArgumentParser(description="Safe Codex quant background worker.")
    parser.add_argument("--once", action="store_true", help="process the queue once and exit")
    parser.add_argument("--loop", action="store_true", help="keep checking the queue")
    parser.add_argument("--interval", type=int, default=None, help="deprecated alias for idle loop seconds")
    parser.add_argument("--idle-interval", type=int, default=600, help="seconds between idle loop checks")
    parser.add_argument("--active-interval", type=int, default=60, help="seconds between active loop checks")
    args = parser.parse_args()
    idle_interval = args.interval if args.interval is not None else args.idle_interval

    if args.once or not args.loop:
        process_once()
        return 0

    append_run_log(
        "worker_started",
        "loop",
        f"idle_poll_interval_seconds={idle_interval}; active_poll_interval_seconds={args.active_interval}",
    )
    while True:
        processed = process_once()
        interval = args.active_interval if processed else idle_interval
        time.sleep(max(interval, 30))


if __name__ == "__main__":
    raise SystemExit(main())
