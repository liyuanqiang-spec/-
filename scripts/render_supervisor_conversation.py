#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


SECRET_PATTERNS = [
    (re.compile(r"sk-[A-Za-z0-9_-]{10,}"), "sk-***"),
    (re.compile(r"gh[pousr]_[A-Za-z0-9_]{10,}"), "gh***"),
    (
        re.compile(r"(?i)\b(api[_-]?key|password|passwd|token|secret|密钥|密码)(\s*[:=]\s*)([^\s`]+)"),
        r"\1\2***",
    ),
]


@dataclass(frozen=True)
class ConversationTask:
    task_id: str
    status: str
    task_type: str
    title: str
    request: str
    result: str


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def redact(text: str) -> str:
    safe = text
    for pattern, replacement in SECRET_PATTERNS:
        safe = pattern.sub(replacement, safe)
    return safe


def one_line(text: str, limit: int = 260) -> str:
    compact = redact(" ".join(text.split()))
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def parse_queue_tasks(text: str) -> list[ConversationTask]:
    tasks: list[ConversationTask] = []
    blocks = re.split(r"(?m)^###\s+", text)
    for block in blocks[1:]:
        lines = block.strip().splitlines()
        if not lines:
            continue
        task_id = lines[0].strip()
        fields: dict[str, str] = {}
        current_key = ""
        for line in lines[1:]:
            match = re.match(r"^-\s*([^:]+):\s*(.*)$", line)
            if match:
                current_key = match.group(1).strip().lower()
                fields[current_key] = match.group(2).strip()
            elif current_key and line.startswith("  "):
                fields[current_key] = f"{fields[current_key]}\n{line.strip()}".strip()
        tasks.append(
            ConversationTask(
                task_id=task_id,
                status=fields.get("status", ""),
                task_type=fields.get("type", ""),
                title=fields.get("title", ""),
                request=fields.get("request", ""),
                result=fields.get("result", ""),
            )
        )
    return tasks


def visible_status_summary(root: Path) -> str:
    lines = [
        line
        for line in read_text(root / "GPT_VISIBLE_STATUS.md").splitlines()
        if line.startswith("- ")
    ][:14]
    if not lines:
        return "- No visible status recorded yet."
    return "\n".join(redact(line) for line in lines)


def recent_run_log(root: Path, limit: int = 8) -> str:
    text = read_text(root / "RUN_LOG.md")
    sections = re.split(r"(?m)^##\s+", text)
    entries: list[str] = []
    for section in sections[1:]:
        lines = section.strip().splitlines()
        if not lines:
            continue
        heading = one_line(lines[0], 120)
        event = ""
        detail = ""
        for line in lines[1:]:
            event_match = re.match(r"^-\s*Event:\s*(.*)$", line)
            detail_match = re.match(r"^-\s*Detail:\s*(.*)$", line)
            if event_match:
                event = one_line(event_match.group(1), 120)
            elif detail_match:
                detail = one_line(detail_match.group(1), 220)
        if event or detail:
            entries.append(f"- `{heading}` {event}: {detail}".rstrip())
    if not entries:
        return "- No run log entries yet."
    return "\n".join(entries[-limit:])


def dialogue_timeline(root: Path, limit: int = 10) -> str:
    tasks = parse_queue_tasks(read_text(root / "TASK_QUEUE.md"))
    if not tasks:
        return "- No GPT tasks found in TASK_QUEUE.md yet."

    parts: list[str] = []
    for task in tasks[-limit:]:
        label = task.title or task.request or task.task_type or "untitled task"
        parts.append(f"### GPT -> Codex: {task.task_id} / {one_line(label, 140)}")
        parts.append(f"- Status: `{one_line(task.status or 'unknown', 80)}`")
        if task.request:
            parts.append(f"- Request: {one_line(task.request)}")
        if task.result:
            parts.append("")
            parts.append(f"### Codex -> GPT: {task.task_id}")
            parts.append(f"- Result: {one_line(task.result)}")
        parts.append("")
    return "\n".join(parts).rstrip()


def local_review_summary(root: Path) -> str:
    text = read_text(root / "GPT_LOCAL_REVIEW_INPUT.md")
    if not text:
        return "- No local GPT review input generated yet."
    lines = [line for line in text.splitlines() if line.startswith("- ")][:12]
    if not lines:
        return "- GPT_LOCAL_REVIEW_INPUT.md exists, but no compact bullet summary was found."
    return "\n".join(redact(line) for line in lines)


def render(root: Path) -> str:
    return (
        "# GPT / Codex Conversation Window\n\n"
        f"Generated at: `{datetime.now().astimezone().isoformat(timespec='seconds')}`\n\n"
        "This file is a read-only progress view. It does not execute tasks.\n\n"
        "## Current Status\n\n"
        f"{visible_status_summary(root)}\n\n"
        "## Dialogue Timeline\n\n"
        f"{dialogue_timeline(root)}\n\n"
        "## Recent Worker Log\n\n"
        f"{recent_run_log(root)}\n\n"
        "## Local GPT Review Input\n\n"
        f"{local_review_summary(root)}\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--output", default="GPT_CODEX_CONVERSATION.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    output = Path(args.output)
    if not output.is_absolute():
        output = root / output
    content = render(root)
    if args.check:
        if "GPT -> Codex" not in content and "No GPT tasks found" not in content:
            print("FAIL: dialogue timeline missing")
            return 1
        print("PASS")
        return 0
    output.write_text(content, encoding="utf-8")
    print(f"rendered {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
