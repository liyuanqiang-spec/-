import sys
import tempfile
import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location(
    "local_review_trigger_dry_run",
    ROOT / "scripts" / "local_review_trigger_dry_run.py",
)
local_review_trigger_dry_run = module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = local_review_trigger_dry_run
SPEC.loader.exec_module(local_review_trigger_dry_run)


class LocalReviewTriggerDryRunTest(unittest.TestCase):
    def make_root(self) -> Path:
        tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(tempdir.cleanup)
        root = Path(tempdir.name)
        (root / "scripts").mkdir()
        (root / "REPORTS").mkdir()
        (root / "logs").mkdir()
        (root / "scripts" / "visible_review_scaffold.py").write_text("# scaffold\n", encoding="utf-8")
        (root / "scripts" / "local_review_trigger_dry_run.py").write_text("# dry run\n", encoding="utf-8")
        (root / "GPT_VISIBLE_REVIEW_STATE.json").write_text(
            '{"state": "SCAFFOLD_READY"}\n',
            encoding="utf-8",
        )
        (root / "GPT_REVIEW.md").write_text(
            """# GPT_REVIEW.md

<!-- visible-review-scaffold:start -->
## Visible Review Scaffold

- State: `SCAFFOLD_READY`
<!-- visible-review-scaffold:end -->
""",
            encoding="utf-8",
        )
        (root / "TASK_QUEUE.md").write_text(
            """# TASK_QUEUE.md

### TASK-016
- Status: completed
- Type: model_review_packet_bridge
- Title: Prepare repository-local model review packet
- Result: codex exec completed

### TASK-017
- Status: completed
- Type: local_review_trigger_dry_run
- Title: Add local post-push review trigger dry run
- Safety: repository_status_only
- Result: codex exec completed
""",
            encoding="utf-8",
        )
        (root / "STATUS.md").write_text("Status: `WORKER_COMPLETED`\n", encoding="utf-8")
        (root / "RUN_LOG.md").write_text(
            "## 2026-06-28 23:59:21 +0800\n\n- Event: completed\n- Detail: Task TASK-017 completed\n",
            encoding="utf-8",
        )
        (root / "DECISION_REQUIRED.md").write_text("# DECISION_REQUIRED.md\n", encoding="utf-8")
        (root / "RISK_CONTROL.md").write_text("# Risk\n", encoding="utf-8")
        (root / "RELIABILITY_RUNBOOK.md").write_text("# Reliability\n", encoding="utf-8")
        (root / "WORKER_DASHBOARD.md").write_text(
            "| Item | Result |\n|---|---|\n| Worker state | IDLE |\n| Visible scaffold | SCAFFOLD_READY |\n",
            encoding="utf-8",
        )
        (root / "GPT_VISIBLE_STATUS.md").write_text(
            """# GPT Visible Status

- Status: `IDLE`
- Visible scaffold: `SCAFFOLD_READY`
- Worker mode: `IDLE`
- Current task: none
- Latest completed task: TASK-017 (completed) - Add local post-push review trigger dry run
- Decision required: none
""",
            encoding="utf-8",
        )
        (root / "GPT_REVIEW_PACKET.md").write_text(
            """# GPT Review Packet

## Current State

- Worker state: `IDLE`
- Latest completed task: TASK-017

## Latest Report Summary

- Source: `REPORTS/latest_report.md`
""",
            encoding="utf-8",
        )
        (root / "REPORTS" / "model_review_packet.md").write_text("# Packet\n", encoding="utf-8")
        return root

    def test_writes_local_review_input_and_visible_marker(self):
        root = self.make_root()
        context = local_review_trigger_dry_run.build_context(root, "Worker processed TASK-017")

        local_review_trigger_dry_run.write_outputs(root, context)

        input_text = (root / "GPT_LOCAL_REVIEW_INPUT.md").read_text(encoding="utf-8")
        review_text = (root / "GPT_REVIEW.md").read_text(encoding="utf-8")
        visible_text = (root / "GPT_VISIBLE_STATUS.md").read_text(encoding="utf-8")
        self.assertIn("LOCAL_REVIEW_TRIGGER_DRY_RUN_READY", input_text)
        self.assertIn("<!-- local-review-trigger-dry-run:start -->", review_text)
        self.assertIn("Local review trigger: `LOCAL_REVIEW_TRIGGER_DRY_RUN_READY`", visible_text)
        ok, errors = local_review_trigger_dry_run.check_outputs(root)
        self.assertTrue(ok, errors)

    def test_redacts_private_paths_and_credentials(self):
        text = "/Users/example/secret api_key = abc123 ghp_abcdefghijkl"
        redacted = local_review_trigger_dry_run.redact(text)
        self.assertNotIn("/Users/example", redacted)
        self.assertNotIn("abc123", redacted)
        self.assertNotIn("ghp_abcdefghijkl", redacted)

    def test_worker_hook_is_disabled_by_default(self):
        worker_text = (ROOT / "scripts" / "codex_worker.sh").read_text(encoding="utf-8")
        self.assertIn('LOCAL_REVIEW_TRIGGER_DRY_RUN_ENABLED="${LOCAL_REVIEW_TRIGGER_DRY_RUN_ENABLED:-0}"', worker_text)
        self.assertIn("run_local_review_trigger_dry_run", worker_text)
        self.assertIn("LOCAL_REVIEW_TRIGGER_DRY_RUN_READY", worker_text)

    def test_worker_generates_review_input_before_final_commit(self):
        worker_text = (ROOT / "scripts" / "codex_worker.sh").read_text(encoding="utf-8")
        review_index = worker_text.index('run_local_review_trigger_dry_run "Worker processed $task_id"')
        commit_index = worker_text.index('commit_and_push "Worker processed $task_id"')
        self.assertLess(review_index, commit_index)
        self.assertIn("before final worker commit", worker_text)
        self.assertNotIn("after successful push", worker_text)


if __name__ == "__main__":
    unittest.main()
