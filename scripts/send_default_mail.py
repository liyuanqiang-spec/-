#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_RECIPIENT_FILE = (
    Path.home()
    / "Library"
    / "Application Support"
    / "CodexGithubWorker"
    / "default_mail_recipient.txt"
)


def read_recipient(path: Path) -> str:
    env_value = os.environ.get("CODEX_DEFAULT_MAIL_RECIPIENT", "").strip()
    if env_value:
        return env_value
    if not path.exists():
        return ""
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    return next((line for line in lines if line and not line.startswith("#")), "")


def recipient_is_valid(value: str) -> bool:
    return bool(value and "@" in value and "\n" not in value and "\r" not in value)


def body_from_args(args: argparse.Namespace) -> str:
    if args.body_file:
        return Path(args.body_file).read_text(encoding="utf-8")
    return args.body or ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", required=True)
    parser.add_argument("--body", default="")
    parser.add_argument("--body-file", default="")
    parser.add_argument("--recipient-file", default=os.environ.get("CODEX_DEFAULT_MAIL_RECIPIENT_FILE", ""))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    recipient_file = Path(args.recipient_file).expanduser() if args.recipient_file else DEFAULT_RECIPIENT_FILE
    recipient = read_recipient(recipient_file)
    if not recipient_is_valid(recipient):
        print("LOCAL_DEFAULT_MAIL_MISSING")
        return 2

    mail_bin = shutil.which("mail") or "/usr/bin/mail"
    if not Path(mail_bin).exists():
        print("LOCAL_DEFAULT_MAIL_UNAVAILABLE")
        return 3

    if args.dry_run:
        print("LOCAL_DEFAULT_MAIL_DRY_RUN_OK")
        return 0

    body = body_from_args(args)
    completed = subprocess.run(
        [mail_bin, "-s", args.subject, recipient],
        input=body,
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if completed.returncode == 0:
        print("LOCAL_DEFAULT_MAIL_SENT")
        return 0
    print("LOCAL_DEFAULT_MAIL_FAILED")
    return completed.returncode or 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
