import tempfile
import sys
import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location(
    "visible_review_scaffold",
    ROOT / "scripts" / "visible_review_scaffold.py",
)
visible_review_scaffold = module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = visible_review_scaffold
SPEC.loader.exec_module(visible_review_scaffold)

REFRESH_SPEC = spec_from_file_location(
    "refresh_visible_status",
    ROOT / "scripts" / "refresh_visible_status.py",
)
refresh_visible_status = module_from_spec(REFRESH_SPEC)
assert REFRESH_SPEC.loader is not None
sys.modules[REFRESH_SPEC.name] = refresh_visible_status
REFRESH_SPEC.loader.exec_module(refresh_visible_status)


class VisibleReviewScaffoldTest(unittest.TestCase):
    def test_unresolved_decisions_ignore_resolved_history(self):
        text = """# DECISION_REQUIRED.md

## Open Decisions

No current user action required for normal safe GitHub status-file supervision.

## Decision Required 2026-06-28 21:25:48 +0800

- Status: resolved
- Item: worker sync failed at pull stage: git pull failed
"""
        self.assertEqual(visible_review_scaffold.unresolved_decisions(text), [])

    def test_redacts_sensitive_assignment_values(self):
        text = "api_key = abc123\npassword: hunter2\nregular: value"
        redacted = visible_review_scaffold.redact(text)
        self.assertNotIn("abc123", redacted)
        self.assertNotIn("hunter2", redacted)
        self.assertIn("regular: value", redacted)

    def test_build_state_ready_when_required_paths_exist(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / "REPORTS").mkdir()
            (root / "src").mkdir()
            (root / "tests").mkdir()
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / ".github" / "workflows" / "visible-review-scaffold.yml").write_text(
                "name: Visible Review Scaffold\n",
                encoding="utf-8",
            )
            (root / "PROJECT_MEMORY.md").write_text("# Memory\n", encoding="utf-8")
            (root / "TASK_QUEUE.md").write_text(
                """# TASK_QUEUE.md

### TASK-013A
- Status: completed
- Type: visible_review_scaffold
- Title: Build safe visible review scaffold
- Result: completed
""",
                encoding="utf-8",
            )
            (root / "STATUS.md").write_text("Status: `TASK_013A_COMPLETED`\n", encoding="utf-8")
            (root / "RUN_LOG.md").write_text(
                "## 2026-06-28 21:00:00 +0800\n\n- Event: completed\n- Detail: ok\n",
                encoding="utf-8",
            )
            (root / "WORKER_DASHBOARD.md").write_text(
                "| Item | Result |\n|---|---|\n| Worker state | IDLE |\n| Current task | None |\n",
                encoding="utf-8",
            )
            (root / "GPT_VISIBLE_STATUS.md").write_text("Status: `IDLE`\n", encoding="utf-8")
            (root / "DECISION_REQUIRED.md").write_text(
                "## Open Decisions\n\nNo current user action required for normal safe GitHub status-file supervision.\n",
                encoding="utf-8",
            )

            state = visible_review_scaffold.build_state(root)

        self.assertEqual(state["state"], "SCAFFOLD_READY")
        self.assertFalse(state["decision_required"]["has_unresolved"])
        visible = visible_review_scaffold.build_visible_status(state)
        self.assertIn("- Visible scaffold: `SCAFFOLD_READY`", visible)

    def test_build_state_busy_even_with_decision_history(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / "REPORTS").mkdir()
            (root / "src").mkdir()
            (root / "tests").mkdir()
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / ".github" / "workflows" / "visible-review-scaffold.yml").write_text(
                "name: Visible Review Scaffold\n",
                encoding="utf-8",
            )
            (root / "PROJECT_MEMORY.md").write_text("# Memory\n", encoding="utf-8")
            (root / "TASK_QUEUE.md").write_text(
                """# TASK_QUEUE.md

### TASK-014
- Status: decision_required
- Type: visible_status_alignment
- Title: Original blocked task
- Result: blocked by risk control

### TASK-014A
- Status: running
- Type: status_display_patch
- Title: Add scaffold state line
- Result: worker started
""",
                encoding="utf-8",
            )
            (root / "STATUS.md").write_text("Status: `WORKER_RUNNING`\n", encoding="utf-8")
            (root / "RUN_LOG.md").write_text(
                "## 2026-06-28 21:55:53 +0800\n\n- Event: started\n- Detail: TASK-014A\n",
                encoding="utf-8",
            )
            (root / "WORKER_DASHBOARD.md").write_text(
                "| Item | Result |\n|---|---|\n| Worker state | WORKING |\n",
                encoding="utf-8",
            )
            (root / "GPT_VISIBLE_STATUS.md").write_text("Status: `WORKING`\n", encoding="utf-8")
            (root / "DECISION_REQUIRED.md").write_text(
                """## Open Decisions

No current user action required for normal safe GitHub status-file supervision.

## Decision Required 2026-06-28 21:49:29 +0800

- Item: Task TASK-014 contains a blocked trading/fund/secret/deletion/danger risk
- Current action: worker stopped before execution
""",
                encoding="utf-8",
            )

            state = visible_review_scaffold.build_state(root)

        self.assertEqual(state["state"], "WORKER_BUSY")
        self.assertTrue(state["decision_required"]["has_unresolved"])

    def test_refresh_visible_status_keeps_scaffold_line(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / "scripts").mkdir()
            (root / "scripts" / "visible_review_scaffold.py").write_text("# script\n", encoding="utf-8")
            (root / "GPT_REVIEW.md").write_text(
                """# GPT_REVIEW.md

<!-- visible-review-scaffold:start -->
## Visible Review Scaffold

- State: `SCAFFOLD_READY`
<!-- visible-review-scaffold:end -->
""",
                encoding="utf-8",
            )
            (root / "GPT_VISIBLE_REVIEW_STATE.json").write_text(
                '{"state": "SCAFFOLD_READY"}\n',
                encoding="utf-8",
            )
            (root / "TASK_QUEUE.md").write_text(
                """# TASK_QUEUE.md

### TASK-014A
- Status: running
- Type: status_display_patch
- Title: Add scaffold state line
- Result: worker started
""",
                encoding="utf-8",
            )
            (root / "STATUS.md").write_text("Status: `WORKER_RUNNING`\n", encoding="utf-8")
            (root / "RUN_LOG.md").write_text("", encoding="utf-8")
            (root / "DECISION_REQUIRED.md").write_text("# DECISION_REQUIRED.md\n", encoding="utf-8")

            state = refresh_visible_status.build_state(root)
            visible = refresh_visible_status.build_gpt_visible_status(state)

        self.assertEqual(state["visible_scaffold"]["state"], "WORKER_BUSY")
        self.assertIn("- Visible scaffold: `WORKER_BUSY`", visible)


if __name__ == "__main__":
    unittest.main()
