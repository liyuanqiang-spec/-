from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .config import (
    DECISION_REQUIRED,
    PROJECT_ROOT,
    RUN_LOG,
    STATUS_FILE,
    TASK_QUEUE,
    WORKER_DASHBOARD,
)


READY_STATUSES = {"pending", "queued", "todo"}


@dataclass(frozen=True)
class DashboardTask:
    task_id: str
    status: str
    task_type: str
    title: str
    request: str
    result: str


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def parse_queue_tasks(text: str) -> list[DashboardTask]:
    tasks: list[DashboardTask] = []
    current_id = ""
    fields: dict[str, str] = {}

    def flush() -> None:
        if not current_id:
            return
        tasks.append(
            DashboardTask(
                task_id=current_id,
                status=fields.get("status", "").strip().lower(),
                task_type=fields.get("type", "").strip(),
                title=fields.get("title", "").strip(),
                request=fields.get("request", "").strip(),
                result=fields.get("result", "").strip(),
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


def _task_summary(task: DashboardTask | None) -> str:
    if task is None:
        return "None"
    label = task.title or task.request or task.task_type or "no title"
    result = f" - {task.result}" if task.result else ""
    return f"`{task.task_id}` ({task.status}) - {label}{result}"


def _last_worker_time(root: Path) -> str:
    heartbeat = root / "logs" / "worker_heartbeat.json"
    if heartbeat.exists():
        try:
            payload = json.loads(heartbeat.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = {}
        timestamp = str(payload.get("timestamp", "")).strip()
        if timestamp:
            return timestamp

    candidates: list[str] = []
    worker_log = root / "logs" / "worker.log"
    for match in re.finditer(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]\d{4})\]", _read_text(worker_log)):
        candidates.append(match.group(1))
    for path in (STATUS_FILE, RUN_LOG):
        text = _read_text(root / path.name)
        for match in re.finditer(r"(?m)^##(?: Worker Update)?\s+(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?: [+-]\d{4}|[+-]\d{2}:\d{2})?)", text):
            candidates.append(match.group(1))
    return candidates[-1] if candidates else "Unknown"


def _latest_status(root: Path) -> str:
    text = _read_text(root / STATUS_FILE.name)
    matches = re.findall(r"(?m)^Status:\s*`?([^`\n]+)`?", text)
    return matches[-1].strip() if matches else "UNKNOWN"


def _latest_commit(root: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "log", "-1", "--format=%h %cs %s"],
            cwd=root,
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return "Unavailable"
    value = completed.stdout.strip()
    return value if completed.returncode == 0 and value else "Unavailable"


def _latest_report(root: Path) -> str:
    reports: dict[Path, Path] = {}
    for dirname in ("reports", "REPORTS"):
        directory = root / dirname
        if not directory.exists():
            continue
        for path in directory.glob("*.md"):
            reports[path.resolve()] = path
    if not reports:
        return "None"
    latest = max(reports.values(), key=lambda path: path.stat().st_mtime)
    rel = latest.relative_to(root).as_posix()
    return f"[`{rel}`]({rel})"


def _latest_completed_task_id(root: Path) -> str:
    text = _read_text(root / RUN_LOG.name)
    matches = re.findall(r"\bTask\s+([A-Za-z0-9_.-]+)\s+completed\b", text)
    return matches[-1] if matches else ""


def _decision_blocker(root: Path) -> str:
    text = _read_text(root / DECISION_REQUIRED.name)
    sections = re.split(r"(?m)^##\s+", text)
    blockers: list[str] = []
    for section in sections:
        if not section.startswith("Decision Required"):
            continue
        if re.search(r"(?mi)^-\s*Status:\s*resolved\s*$", section):
            continue
        item = re.search(r"(?mi)^-\s*Item:\s*(.+)$", section)
        task = re.search(r"(?mi)^-\s*Task:\s*(.+)$", section)
        reason = re.search(r"(?mi)^-\s*Block reason:\s*(.+)$", section)
        detail = item or task or reason
        blockers.append(detail.group(1).strip() if detail else section.splitlines()[0].strip())
    if not blockers:
        return "No"
    return f"Yes - {blockers[-1]}"


def _cell(value: str) -> str:
    return value.replace("\n", " ").replace("|", "/").strip()


def build_dashboard(root: Path = PROJECT_ROOT) -> str:
    queue_text = _read_text(root / TASK_QUEUE.name)
    tasks = parse_queue_tasks(queue_text)
    running = next((task for task in tasks if task.status == "running"), None)
    pending = next((task for task in tasks if task.status in READY_STATUSES), None)
    latest_completed_id = _latest_completed_task_id(root)
    completed = next(
        (
            task
            for task in tasks
            if task.status == "completed" and task.task_id == latest_completed_id
        ),
        None,
    ) or next((task for task in reversed(tasks) if task.status == "completed"), None)
    failed = next(
        (task for task in reversed(tasks) if task.status in {"failed", "decision_required"}),
        None,
    )
    decision = _decision_blocker(root)
    latest_status = _latest_status(root)

    if running:
        worker_state = f"RUNNING - latest status `{latest_status}`"
    elif decision.startswith("Yes"):
        worker_state = f"ATTENTION - latest status `{latest_status}`"
    elif pending:
        worker_state = f"WAITING_FOR_NEXT_SCAN - latest status `{latest_status}`"
    else:
        worker_state = f"IDLE - latest status `{latest_status}`"

    if decision.startswith("Yes"):
        next_step = "Resolve or rewrite the item in `DECISION_REQUIRED.md`; keep normal safe report/status tasks in simulation mode."
    elif running:
        next_step = "Let the current task finish; this dashboard refreshes at the end of each worker scan."
    elif pending:
        next_step = "Worker will execute the next pending safe task on the next scheduled scan."
    else:
        next_step = "Add the next safe data, backtest, simulation, or report task to `TASK_QUEUE.md`."

    generated_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    rows = [
        ("Last heartbeat time", _last_worker_time(root)),
        ("Worker status", worker_state),
        ("Current task", _task_summary(running or pending)),
        ("Recently completed task", _task_summary(completed)),
        ("Recent failed or blocked task", _task_summary(failed)),
        ("Latest report link", _latest_report(root)),
        ("Latest push/commit", _latest_commit(root)),
        ("DECISION_REQUIRED blocking", decision),
        ("Current safety mode", "`PHASE_1_SIMULATION_ONLY`"),
        ("Next recommendation", next_step),
    ]
    table = "\n".join(f"| {_cell(key)} | {_cell(value)} |" for key, value in rows)
    return (
        "# Worker Dashboard\n\n"
        f"Last dashboard update: `{generated_at}`\n\n"
        "| Item | Result |\n"
        "|---|---|\n"
        f"{table}\n\n"
        "## Links\n\n"
        "- [Task queue](TASK_QUEUE.md)\n"
        "- [Status](STATUS.md)\n"
        "- [Run log](RUN_LOG.md)\n"
        "- [Decision required](DECISION_REQUIRED.md)\n"
        "- [Risk control](RISK_CONTROL.md)\n"
    )


def update_dashboard(root: Path = PROJECT_ROOT) -> Path:
    dashboard = root / WORKER_DASHBOARD.name
    dashboard.write_text(build_dashboard(root), encoding="utf-8")
    return dashboard
