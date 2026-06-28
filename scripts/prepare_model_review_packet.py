#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


SAFETY_MODE = "PHASE_1_SIMULATION_ONLY"
PACKET_FILE = "GPT_REVIEW_PACKET.md"
REPORT_PACKET_FILE = "REPORTS/model_review_packet.md"
REVIEW_START = "<!-- model-review-packet:start -->"
REVIEW_END = "<!-- model-review-packet:end -->"
MAX_TEXT_BYTES = 100_000
MAX_SUMMARY_ITEMS = 5

ROOT_INPUT_FILES = [
    "GPT_REVIEW.md",
    "GPT_VISIBLE_STATUS.md",
    "WORKER_DASHBOARD.md",
    "STATUS.md",
    "RUN_LOG.md",
    "DECISION_REQUIRED.md",
    "QUANT_SYSTEM_TARGETS.md",
]

GENERATED_REPORT_NAMES = {"model_review_packet.md"}

SENSITIVE_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{8,}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{8,}\b"),
    re.compile(
        r"(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|secret|password|authorization|credential)"
        r"(\s*[:=]\s*)(['\"]?)[^'\"\s]+"
    ),
    re.compile(r"/Users/[^\s`'\"),]+"),
    re.compile(r"/private/[^\s`'\"),]+"),
]


@dataclass(frozen=True)
class PacketContext:
    generated_at: str
    scaffold_state: str
    worker_state: str
    current_task: str
    latest_completed_task: str
    unresolved_blocker: str
    latest_report_path: str
    latest_report_summary: list[str]
    quant_gap_summary: list[str]
    next_tasks: list[str]


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def redact(text: str) -> str:
    redacted = text
    redacted = SENSITIVE_PATTERNS[0].sub("sk-[REDACTED]", redacted)
    redacted = SENSITIVE_PATTERNS[1].sub("gh-[REDACTED]", redacted)
    redacted = SENSITIVE_PATTERNS[2].sub("AIza[REDACTED]", redacted)
    redacted = SENSITIVE_PATTERNS[3].sub(lambda m: f"{m.group(1)}{m.group(2)}[REDACTED]", redacted)
    redacted = SENSITIVE_PATTERNS[4].sub("[LOCAL_PATH]", redacted)
    redacted = SENSITIVE_PATTERNS[5].sub("[LOCAL_PATH]", redacted)
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


def section_body(text: str, heading: str) -> str:
    pattern = rf"(?ms)^##\s+{re.escape(heading)}\s*\n(?P<body>.*?)(?=^##\s+|\Z)"
    match = re.search(pattern, text)
    return match.group("body").strip() if match else ""


def bullet_lines(text: str, limit: int = MAX_SUMMARY_ITEMS) -> list[str]:
    values: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^\s*[-*]\s+(.+)$", line)
        if match:
            values.append(one_line(match.group(1), 240))
        if len(values) >= limit:
            break
    return values


def numbered_lines(text: str, limit: int = 3) -> list[str]:
    values: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^\s*\d+\.\s+(.+)$", line)
        if not match:
            continue
        item = re.sub(r"^TASK-\d+[A-Z]?:\s*", "", match.group(1).strip())
        values.append(one_line(item, 240))
        if len(values) >= limit:
            break
    return values


def first_heading(text: str) -> str:
    match = re.search(r"(?m)^#\s+(.+)$", text)
    return one_line(match.group(1), 160) if match else ""


def conclusion_line(text: str) -> str:
    for line in text.splitlines():
        cleaned = line.strip()
        if cleaned.startswith("结论"):
            return one_line(cleaned, 240)
    for paragraph in re.split(r"\n\s*\n", text):
        cleaned = one_line(paragraph, 240)
        if cleaned and not cleaned.startswith("#"):
            return cleaned
    return ""


def markdown_table_metrics(text: str, limit: int = MAX_SUMMARY_ITEMS) -> list[str]:
    values: list[str] = []
    for line in text.splitlines():
        if not line.startswith("|") or "---" in line:
            continue
        cells = [one_line(cell.strip(), 120) for cell in line.strip("|").split("|")]
        if len(cells) >= 2 and cells[0].lower() not in {"metric", "item", "check"}:
            values.append(f"{cells[0]}: {cells[1]}")
        if len(values) >= limit:
            break
    return values


def report_files(root: Path) -> list[Path]:
    reports = root / "REPORTS"
    if not reports.exists() or not reports.is_dir():
        return []
    return sorted(
        path
        for path in reports.glob("*.md")
        if path.is_file() and path.name not in GENERATED_REPORT_NAMES
    )


def latest_report_path(root: Path, dashboard_text: str) -> Path | None:
    dashboard_report = table_value(dashboard_text, "Latest report")
    if dashboard_report and not Path(dashboard_report).name in GENERATED_REPORT_NAMES:
        candidate = root / dashboard_report
        if candidate.is_file() and candidate.suffix == ".md" and candidate.parent.name == "REPORTS":
            return candidate
    files = report_files(root)
    if not files:
        return None
    return max(files, key=lambda path: path.stat().st_mtime)


def summarize_report(path: Path | None, root: Path) -> tuple[str, list[str]]:
    if path is None:
        return "none", ["No markdown report found under REPORTS."]
    text = read_text(path)
    rel = path.relative_to(root).as_posix()
    summary: list[str] = []
    heading = first_heading(text)
    if heading:
        summary.append(f"Title: {heading}")
    conclusion = conclusion_line(text)
    if conclusion:
        summary.append(conclusion)
    summary.extend(bullet_lines(section_body(text, "Summary"), 3))
    if len(summary) < MAX_SUMMARY_ITEMS:
        summary.extend(markdown_table_metrics(section_body(text, "Result Table"), MAX_SUMMARY_ITEMS - len(summary)))
    if len(summary) < MAX_SUMMARY_ITEMS:
        summary.extend(markdown_table_metrics(text, MAX_SUMMARY_ITEMS - len(summary)))
    return rel, summary[:MAX_SUMMARY_ITEMS] or ["Report exists but no concise summary lines were found."]


def summarize_quant_gap(root: Path) -> list[str]:
    gap_path = root / "REPORTS" / "quant_system_gap_report.md"
    target_path = root / "QUANT_SYSTEM_TARGETS.md"
    gap_text = read_text(gap_path)
    target_text = read_text(target_path)
    summary: list[str] = []
    if gap_text:
        conclusion = conclusion_line(gap_text)
        if conclusion:
            summary.append(conclusion)
        key_question = section_body(gap_text, "Can It Answer The Key Question?")
        if key_question:
            first = conclusion_line(key_question) or one_line(key_question, 240)
            if first:
                summary.append(first)
        remaining = bullet_lines(section_body(gap_text, "Remaining Gaps"), 3)
        summary.extend(f"Gap: {item}" for item in remaining)
    if not summary and target_text:
        north_star = section_body(target_text, "1. North star")
        immediate = section_body(target_text, "7. Immediate P0 target")
        summary.extend(filter(None, [one_line(north_star, 240), one_line(immediate, 240)]))
    return summary[:MAX_SUMMARY_ITEMS] or ["Quant-system gap report is not available."]


def next_safe_tasks(root: Path) -> list[str]:
    gap_text = read_text(root / "REPORTS" / "quant_system_gap_report.md")
    tasks = numbered_lines(section_body(gap_text, "Next Three Safe Codex Tasks"), 3)
    if len(tasks) >= 3:
        return tasks
    defaults = [
        "Add parameter sensitivity report for passive fill threshold, timeout, second-leg adverse move, fee, and slippage assumptions.",
        "Extend the repository report/dashboard layer with time-value anomalies, spread rankings, and replay summary links.",
        "Add a repository-local fill-event fixture to validate passive-fill and incomplete-leg assumptions without broker access.",
    ]
    merged = tasks[:]
    for item in defaults:
        if item not in merged:
            merged.append(item)
        if len(merged) == 3:
            break
    return merged


def unresolved_blocker(visible_text: str, decision_text: str) -> str:
    visible_decision = visible_value(visible_text, "Decision required")
    if visible_decision and visible_decision.lower() not in {"none", "no unresolved item"}:
        return visible_decision

    open_body = section_body(decision_text, "Open Decisions")
    if open_body and "No current user action required" not in open_body:
        lines = bullet_lines(open_body, 3)
        if lines:
            return "; ".join(lines)
        return one_line(open_body)
    return "none"


def build_context(root: Path) -> PacketContext:
    visible = read_text(root / "GPT_VISIBLE_STATUS.md")
    dashboard = read_text(root / "WORKER_DASHBOARD.md")
    decisions = read_text(root / "DECISION_REQUIRED.md")
    report_path = latest_report_path(root, dashboard)
    latest_report, report_summary = summarize_report(report_path, root)
    return PacketContext(
        generated_at=now_iso(),
        scaffold_state=visible_value(visible, "Visible scaffold") or table_value(dashboard, "Visible scaffold") or "UNKNOWN",
        worker_state=visible_value(visible, "Status") or table_value(dashboard, "Worker state") or "UNKNOWN",
        current_task=visible_value(visible, "Current task") or table_value(dashboard, "Current task") or "none",
        latest_completed_task=visible_value(visible, "Latest completed task")
        or table_value(dashboard, "Latest completed task")
        or "none",
        unresolved_blocker=unresolved_blocker(visible, decisions),
        latest_report_path=latest_report,
        latest_report_summary=report_summary,
        quant_gap_summary=summarize_quant_gap(root),
        next_tasks=next_safe_tasks(root),
    )


def markdown_list(items: list[str]) -> str:
    return "\n".join(f"- {one_line(item, 260)}" for item in items)


def numbered_markdown(items: list[str]) -> str:
    return "\n".join(f"{index}. {one_line(item, 260)}" for index, item in enumerate(items, start=1))


def build_packet(context: PacketContext) -> str:
    return (
        "# GPT Review Packet\n\n"
        f"- Generated at: `{context.generated_at}`\n"
        f"- Safety mode: `{SAFETY_MODE}`\n"
        "- Scope: repository-local status and report Markdown only; no outside service calls.\n"
        "- Exclusions: no raw data dump, no environment variables, no private absolute paths, no credential-like values.\n\n"
        "## Current State\n\n"
        f"- Current scaffold state: `{context.scaffold_state}`\n"
        f"- Worker state: `{context.worker_state}`\n"
        f"- Current task: {context.current_task}\n"
        f"- Latest completed task: {context.latest_completed_task}\n"
        f"- Unresolved blocker: {context.unresolved_blocker}\n\n"
        "## Latest Report Summary\n\n"
        f"- Source: `{context.latest_report_path}`\n"
        f"{markdown_list(context.latest_report_summary)}\n\n"
        "## Quant-System Gap Summary\n\n"
        f"{markdown_list(context.quant_gap_summary)}\n\n"
        "## Next Three Safe Repository Tasks\n\n"
        f"{numbered_markdown(context.next_tasks)}\n\n"
        "## Review Focus\n\n"
        "- Confirm that the next queue item remains repository-local and simulation-only.\n"
        "- Prefer parameter sensitivity, report/dashboard visibility, and local fixture validation before any live-data or account-dependent work.\n"
    )


def build_review_block(context: PacketContext) -> str:
    next_tasks = "; ".join(context.next_tasks)
    return (
        f"{REVIEW_START}\n"
        "## Model Review Packet Bridge\n\n"
        f"- Generated at: `{context.generated_at}`\n"
        f"- Packet: `{PACKET_FILE}`\n"
        f"- Report copy: `{REPORT_PACKET_FILE}`\n"
        f"- Scaffold state: `{context.scaffold_state}`\n"
        f"- Worker state: `{context.worker_state}`\n"
        f"- Latest completed task: {context.latest_completed_task}\n"
        f"- Unresolved blocker: {context.unresolved_blocker}\n"
        f"- Next safe repository tasks: {one_line(next_tasks, 360)}\n"
        f"{REVIEW_END}\n"
    )


def refresh_review_file(root: Path, context: PacketContext) -> None:
    path = root / "GPT_REVIEW.md"
    existing = read_text(path, max_bytes=500_000)
    block = build_review_block(context)
    if REVIEW_START in existing and REVIEW_END in existing:
        pattern = re.compile(rf"{re.escape(REVIEW_START)}.*?{re.escape(REVIEW_END)}", re.DOTALL)
        updated = pattern.sub(block.strip(), existing)
    else:
        updated = existing.rstrip() + "\n\n" + block
    path.write_text(updated.rstrip() + "\n", encoding="utf-8")


def write_outputs(root: Path, context: PacketContext) -> None:
    packet = build_packet(context)
    (root / PACKET_FILE).write_text(packet, encoding="utf-8")
    report_path = root / REPORT_PACKET_FILE
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(packet, encoding="utf-8")
    refresh_review_file(root, context)


def check_outputs(root: Path) -> tuple[bool, list[str]]:
    errors: list[str] = []
    for rel in ROOT_INPUT_FILES:
        if not (root / rel).is_file():
            errors.append(f"missing input file: {rel}")
    for rel in (PACKET_FILE, REPORT_PACKET_FILE):
        path = root / rel
        if not path.is_file():
            errors.append(f"missing packet file: {rel}")
            continue
        text = read_text(path, max_bytes=500_000)
        for required in (
            "## Current State",
            "## Latest Report Summary",
            "## Quant-System Gap Summary",
            "## Next Three Safe Repository Tasks",
        ):
            if required not in text:
                errors.append(f"{rel} missing section: {required}")
        if re.search(r"/Users/|/private/|sk-[A-Za-z0-9_-]{8,}|gh[pousr]_[A-Za-z0-9_]{8,}", text):
            errors.append(f"{rel} contains unredacted private path or credential-like token")
    review = read_text(root / "GPT_REVIEW.md", max_bytes=500_000)
    if REVIEW_START not in review or REVIEW_END not in review:
        errors.append("GPT_REVIEW.md missing model review packet markers")
    return not errors, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare a repository-local GPT model review packet.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
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

    context = build_context(root)
    write_outputs(root, context)
    if not args.quiet:
        print(f"prepared model review packet: {PACKET_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
