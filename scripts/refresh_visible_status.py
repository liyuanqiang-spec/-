#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


READY_STATUSES = {"pending", "queued", "todo"}
RUNNING_STATUSES = {"running"}
COMPLETED_STATUSES = {"completed"}
VISIBLE_REVIEW_START = "<!-- visible-review-scaffold:start -->"
VISIBLE_REVIEW_END = "<!-- visible-review-scaffold:end -->"
VISIBLE_SCAFFOLD_STATES = {"SCAFFOLD_READY", "WORKER_BUSY", "FAILED_WITH_REASON"}
REQUIRED_FILES = [
    "AGENTS.md",
    "TASK_QUEUE.md",
    "STATUS.md",
    "RUN_LOG.md",
    "DECISION_REQUIRED.md",
    "RISK_CONTROL.md",
    "RELIABILITY_RUNBOOK.md",
    "WORKER_DASHBOARD.md",
    "GPT_VISIBLE_STATUS.md",
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
            "request": self.request,
            "result": self.result,
            "safety": self.safety,
        }


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def now_text() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


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


def unresolved_decisions(text: str) -> list[str]:
    sections = re.split(r"(?m)^##\s+", text)
    unresolved: list[str] = []

    def add_detail(section: str, default: str) -> None:
        item = re.search(r"(?mi)^-\s*Item:\s*(.+)$", section)
        task = re.search(r"(?mi)^-\s*Task:\s*(.+)$", section)
        reason = re.search(r"(?mi)^-\s*Block reason:\s*(.+)$", section)
        detail = item or task or reason
        value = (detail.group(1).strip() if detail else default)[:240]
        if value not in unresolved:
            unresolved.append(value)

    for section in sections:
        title = section.splitlines()[0].strip() if section.splitlines() else ""
        if not title.startswith("Decision Required"):
            continue
        if re.search(r"(?mi)^-\s*Status:\s*resolved\s*$", section):
            continue
        add_detail(section, title)

    for match in re.finditer(r"(?ms)^###\s+([^\n]+)\n(.*?)(?=^###\s+|^##\s+|\Z)", text):
        title = match.group(1).strip()
        section = match.group(2)
        if re.search(r"(?mi)^-\s*Status:\s*resolved\s*$", section):
            continue
        if re.search(r"(?mi)^-\s*Status:\s*(open|pending|decision_required)\s*$", section):
            add_detail(section, title)
    return unresolved


def latest_status(root: Path) -> str:
    matches = re.findall(r"(?m)^Status:\s*`?([^`\n]+)`?", read_text(root / "STATUS.md"))
    return matches[-1].strip() if matches else "UNKNOWN"


def latest_commit(root: Path) -> str:
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


def last_worker_check(root: Path) -> str:
    heartbeat = root / "logs" / "worker_heartbeat.json"
    if heartbeat.exists():
        try:
            payload = json.loads(heartbeat.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = {}
        timestamp = str(payload.get("timestamp", "")).strip()
        state = str(payload.get("state", "")).strip()
        task = str(payload.get("task", "")).strip()
        if timestamp:
            suffix = ""
            if state:
                suffix += f" / {state}"
            if task and task != "none":
                suffix += f" / {task}"
            return timestamp + suffix

    candidates: list[str] = []
    for rel in ("RUN_LOG.md", "STATUS.md"):
        text = read_text(root / rel)
        for match in re.finditer(
            r"(?m)^##(?: Worker Update)?\s+(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?: [+-]\d{4}|[+-]\d{2}:\d{2})?)",
            text,
        ):
            candidates.append(match.group(1))
    return candidates[-1] if candidates else "unknown"


def latest_report(root: Path) -> str:
    candidates: list[Path] = []
    for dirname in ("REPORTS", "reports"):
        directory = root / dirname
        if directory.exists():
            candidates.extend(path for path in directory.glob("*.md") if path.is_file())
    if not candidates:
        return "None"
    latest = max(candidates, key=lambda path: path.stat().st_mtime)
    return latest.relative_to(root).as_posix()


def worker_poll_intervals(root: Path) -> dict[str, int | str]:
    worker_script = read_text(root / "scripts" / "codex_worker.sh")
    idle_match = re.search(r"WORKER_IDLE_POLL_INTERVAL_SECONDS:-(\d+)", worker_script)
    active_match = re.search(r"WORKER_ACTIVE_POLL_INTERVAL_SECONDS:-(\d+)", worker_script)
    idle: int | None = int(idle_match.group(1)) if idle_match else None
    active: int | None = int(active_match.group(1)) if active_match else None

    heartbeat = root / "logs" / "worker_heartbeat.json"
    if heartbeat.exists():
        try:
            payload = json.loads(heartbeat.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = {}
        if idle is None and payload.get("idle_poll_interval_seconds") is not None:
            idle = int(payload["idle_poll_interval_seconds"])
        if active is None and payload.get("active_poll_interval_seconds") is not None:
            active = int(payload["active_poll_interval_seconds"])

    return {
        "idle_seconds": idle if idle is not None else "unknown",
        "active_seconds": active if active is not None else "unknown",
    }


def visible_review_block_state(text: str) -> str:
    pattern = re.compile(
        rf"{re.escape(VISIBLE_REVIEW_START)}(?P<body>.*?){re.escape(VISIBLE_REVIEW_END)}",
        re.DOTALL,
    )
    matches = list(pattern.finditer(text))
    if not matches:
        return ""
    body = matches[-1].group("body")
    match = re.search(r"(?m)^-\s*State:\s*`?([A-Z_]+)`?", body)
    return match.group(1) if match and match.group(1) in VISIBLE_SCAFFOLD_STATES else ""


def visible_scaffold_state(root: Path, running: QueueTask | None) -> dict[str, str]:
    missing = [
        rel
        for rel in (
            "scripts/visible_review_scaffold.py",
            "GPT_REVIEW.md",
            "GPT_VISIBLE_REVIEW_STATE.json",
        )
        if not (root / rel).is_file()
    ]
    if missing:
        return {
            "state": "FAILED_WITH_REASON",
            "reason": "missing visible scaffold files: " + ", ".join(missing),
        }

    review_state = visible_review_block_state(read_text(root / "GPT_REVIEW.md"))
    if not review_state:
        return {
            "state": "FAILED_WITH_REASON",
            "reason": "GPT_REVIEW.md is missing a visible review scaffold block",
        }

    try:
        saved = json.loads((root / "GPT_VISIBLE_REVIEW_STATE.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "state": "FAILED_WITH_REASON",
            "reason": f"GPT_VISIBLE_REVIEW_STATE.json is invalid: {exc}",
        }
    saved_state = str(saved.get("state", ""))
    if saved_state not in VISIBLE_SCAFFOLD_STATES:
        return {
            "state": "FAILED_WITH_REASON",
            "reason": "GPT_VISIBLE_REVIEW_STATE.json has no valid scaffold state",
        }
    if "FAILED_WITH_REASON" in {review_state, saved_state}:
        return {
            "state": "FAILED_WITH_REASON",
            "reason": "latest visible scaffold artifact recorded a failure",
        }
    if running:
        return {"state": "WORKER_BUSY", "reason": "current worker task is running"}
    return {"state": "SCAFFOLD_READY", "reason": "visible scaffold artifacts are present"}


def task_summary(task: QueueTask | None) -> str:
    if task is None:
        return "None"
    label = task.title or task.request or task.task_type or "no title"
    result = f" | {task.result}" if task.result else ""
    return f"{task.task_id} ({task.status}) - {label}{result}"


def cell(value: str) -> str:
    return value.replace("\n", " ").replace("|", "/").strip()


def build_state(root: Path) -> dict[str, Any]:
    tasks = parse_queue_tasks(read_text(root / "TASK_QUEUE.md"))
    running = next((task for task in tasks if task.status in RUNNING_STATUSES), None)
    pending = next((task for task in tasks if task.status in READY_STATUSES), None)
    current = running or pending
    completed = next((task for task in reversed(tasks) if task.status in COMPLETED_STATUSES), None)
    failed = next(
        (task for task in reversed(tasks) if task.status in {"failed", "decision_required"}),
        None,
    )
    decisions = unresolved_decisions(read_text(root / "DECISION_REQUIRED.md"))
    if running:
        state = "WORKING"
    elif decisions:
        state = "BLOCKED"
    elif pending:
        state = "WAITING_FOR_WORKER"
    else:
        state = "IDLE"

    if state == "BLOCKED":
        next_action = "人工处理 DECISION_REQUIRED.md 中未解决事项，然后重新刷新状态。"
    elif state == "WORKING":
        next_action = "等待当前任务完成；worker 会在完成、失败或阻塞后推送状态。"
    elif state == "WAITING_FOR_WORKER":
        next_action = "本机 worker 下一轮应执行第一个待处理安全任务。"
    else:
        next_action = "ChatGPT 可以向 TASK_QUEUE.md 写入下一项安全任务。"

    return {
        "generated_at": now_iso(),
        "state": state,
        "visible_scaffold": visible_scaffold_state(root, running),
        "safety_mode": "PHASE_1_SIMULATION_ONLY",
        "latest_status": latest_status(root),
        "latest_commit": latest_commit(root),
        "last_worker_check": last_worker_check(root),
        "latest_report": latest_report(root),
        "worker_poll_intervals": worker_poll_intervals(root),
        "current_task": current.to_state() if current else None,
        "first_running_task": running.to_state() if running else None,
        "first_pending_task": pending.to_state() if pending else None,
        "latest_completed_task": completed.to_state() if completed else None,
        "latest_failed_or_blocked_task": failed.to_state() if failed else None,
        "decision_required": {
            "has_unresolved": bool(decisions),
            "items": decisions,
        },
        "next_action": next_action,
    }


def build_dashboard(state: dict[str, Any]) -> str:
    current = state["current_task"]
    completed = state["latest_completed_task"]
    failed = state["latest_failed_or_blocked_task"]
    decision = state["decision_required"]
    decision_text = (
        "Yes - " + "; ".join(decision["items"])
        if decision["has_unresolved"]
        else "No unresolved item"
    )
    rows = [
        ("Worker state", state["state"]),
        ("Visible scaffold", state["visible_scaffold"]["state"]),
        ("Current task", task_summary_from_state(current)),
        ("First pending task", task_summary_from_state(state["first_pending_task"])),
        ("Latest completed task", task_summary_from_state(completed)),
        ("Latest failed or blocked task", task_summary_from_state(failed)),
        ("Latest status", state["latest_status"]),
        ("Last worker check", state["last_worker_check"]),
        ("Latest report", state["latest_report"]),
        ("Latest push/commit", state["latest_commit"]),
        (
            "Worker poll interval",
            f"idle {state['worker_poll_intervals']['idle_seconds']}s, "
            f"active {state['worker_poll_intervals']['active_seconds']}s",
        ),
        ("Decision required", decision_text),
        ("Safety mode", state["safety_mode"]),
        ("Next action", state["next_action"]),
    ]
    table = "\n".join(f"| {cell(key)} | {cell(value)} |" for key, value in rows)
    return (
        "# Worker Dashboard\n\n"
        f"Last dashboard update: `{now_text()}`\n\n"
        "| Item | Result |\n"
        "|---|---|\n"
        f"{table}\n\n"
        "## Links\n\n"
        "- [Task queue](TASK_QUEUE.md)\n"
        "- [Status](STATUS.md)\n"
        "- [Run log](RUN_LOG.md)\n"
        "- [Decision required](DECISION_REQUIRED.md)\n"
        "- [Risk control](RISK_CONTROL.md)\n"
        "- [Reliability runbook](RELIABILITY_RUNBOOK.md)\n"
        "- [GPT visible status](GPT_VISIBLE_STATUS.md)\n"
    )


def task_summary_from_state(task: dict[str, str] | None) -> str:
    if not task:
        return "None"
    label = task.get("title") or task.get("request") or task.get("type") or "no title"
    result = f" | {task.get('result')}" if task.get("result") else ""
    return f"{task.get('id')} ({task.get('status')}) - {label}{result}"


def build_gpt_visible_status(state: dict[str, Any]) -> str:
    decision = state["decision_required"]
    current = state["current_task"]
    if decision["has_unresolved"]:
        decision_text = "yes - " + "; ".join(decision["items"])
    else:
        decision_text = "none"
    if current:
        task_text = (
            f"{current['id']} / {current['status']} / "
            f"{current.get('title') or current.get('request') or current.get('type')}"
        )
    else:
        task_text = "none"
    return (
        "# GPT Visible Status\n\n"
        f"- Generated at: `{state['generated_at']}`\n"
        f"- Status: `{state['state']}`\n"
        f"- Visible scaffold: `{state['visible_scaffold']['state']}`\n"
        f"- Safety mode: `{state['safety_mode']}`\n"
        f"- Current task: {task_text}\n"
        f"- Latest completed task: {task_summary_from_state(state['latest_completed_task'])}\n"
        f"- Decision required: {decision_text}\n"
        f"- Latest status marker: `{state['latest_status']}`\n"
        f"- Last worker check: {state['last_worker_check']}\n"
        f"- Latest commit: {state['latest_commit']}\n"
        f"- Worker poll interval: idle {state['worker_poll_intervals']['idle_seconds']}s, active {state['worker_poll_intervals']['active_seconds']}s\n"
        f"- Next action: {state['next_action']}\n\n"
        "## ChatGPT Supervision Contract\n\n"
        "- ChatGPT writes safe work into `TASK_QUEUE.md`.\n"
        "- The Mac mini worker pulls `main`, executes safe repository work, refreshes status files, commits, and pushes back.\n"
        "- `DECISION_REQUIRED.md` is only for unresolved human decisions; resolved history must not change the visible state.\n"
    )


def append_review(root: Path, message: str, state: dict[str, Any]) -> bool:
    if not message:
        return False
    path = root / "GPT_REVIEW.md"
    text = read_text(path)
    if message in text:
        return False
    entry = (
        f"\n## {now_text()}\n\n"
        f"- {message}\n"
        f"- Visible state: `{state['state']}`\n"
        f"- Current task: {task_summary_from_state(state['current_task'])}\n"
        f"- Decision required: "
        f"{'yes' if state['decision_required']['has_unresolved'] else 'none'}\n"
    )
    if not text:
        text = "# GPT_REVIEW.md\n"
    path.write_text(text.rstrip() + "\n" + entry, encoding="utf-8")
    return True


def write_outputs(root: Path, state: dict[str, Any], review_message: str = "") -> None:
    (root / "WORKER_DASHBOARD.md").write_text(build_dashboard(state), encoding="utf-8")
    (root / "GPT_VISIBLE_STATUS.md").write_text(build_gpt_visible_status(state), encoding="utf-8")
    (root / ".gpt_state.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    append_review(root, review_message, state)


def check_outputs(root: Path) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            reasons.append(f"missing required file: {rel}")

    state = build_state(root)
    dashboard = read_text(root / "WORKER_DASHBOARD.md")
    visible = read_text(root / "GPT_VISIBLE_STATUS.md")
    state_file = root / ".gpt_state.json"
    if not state_file.exists():
        reasons.append("missing state file: .gpt_state.json")
        saved_state: dict[str, Any] = {}
    else:
        try:
            saved_state = json.loads(state_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            saved_state = {}
            reasons.append(f".gpt_state.json is not valid JSON: {exc}")

    expected_state = state["state"]
    if expected_state not in dashboard:
        reasons.append(f"WORKER_DASHBOARD.md does not show state {expected_state}")
    if f"Status: `{expected_state}`" not in visible:
        reasons.append(f"GPT_VISIBLE_STATUS.md does not show Status: `{expected_state}`")
    expected_scaffold = state["visible_scaffold"]["state"]
    if f"Visible scaffold: `{expected_scaffold}`" not in visible:
        reasons.append(f"GPT_VISIBLE_STATUS.md does not show Visible scaffold: `{expected_scaffold}`")
    if expected_scaffold not in dashboard:
        reasons.append(f"WORKER_DASHBOARD.md does not show visible scaffold state {expected_scaffold}")
    if saved_state.get("state") != expected_state:
        reasons.append(".gpt_state.json state does not match queue/decision state")
    if saved_state.get("visible_scaffold", {}).get("state") != expected_scaffold:
        reasons.append(".gpt_state.json visible scaffold state does not match repository state")

    current = state["current_task"]
    if expected_state in {"WORKING", "WAITING_FOR_WORKER"} and current:
        for field_name in ("id", "status"):
            value = current[field_name]
            if value not in dashboard:
                reasons.append(f"WORKER_DASHBOARD.md missing current task {field_name}: {value}")
            if value not in visible:
                reasons.append(f"GPT_VISIBLE_STATUS.md missing current task {field_name}: {value}")

    if not state["decision_required"]["has_unresolved"]:
        if "ATTENTION" in dashboard or "ATTENTION" in visible:
            reasons.append("resolved historical decisions are still creating ATTENTION state")
        if saved_state.get("decision_required", {}).get("has_unresolved") is True:
            reasons.append(".gpt_state.json marks a resolved decision as unresolved")

    return not reasons, reasons


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--append-review-note", default="")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if args.check:
        ok, reasons = check_outputs(root)
        if ok:
            print("PASS")
            return 0
        print("FAIL")
        for reason in reasons:
            print(f"- {reason}")
        return 1

    state = build_state(root)
    write_outputs(root, state, args.append_review_note)
    if not args.quiet:
        print(f"refreshed visible status: {state['state']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
