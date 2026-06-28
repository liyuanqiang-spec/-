import sys
import tempfile
import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location(
    "prepare_model_review_packet",
    ROOT / "scripts" / "prepare_model_review_packet.py",
)
prepare_model_review_packet = module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = prepare_model_review_packet
SPEC.loader.exec_module(prepare_model_review_packet)


class ModelReviewPacketTest(unittest.TestCase):
    def make_root(self) -> Path:
        tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(tempdir.cleanup)
        root = Path(tempdir.name)
        (root / "REPORTS").mkdir()
        (root / "GPT_REVIEW.md").write_text("# GPT_REVIEW.md\n", encoding="utf-8")
        (root / "GPT_VISIBLE_STATUS.md").write_text(
            """# GPT Visible Status

- Status: `IDLE`
- Visible scaffold: `SCAFFOLD_READY`
- Current task: none
- Latest completed task: TASK-015 (completed) - Adaptive polling
- Decision required: none
""",
            encoding="utf-8",
        )
        (root / "WORKER_DASHBOARD.md").write_text(
            """# Worker Dashboard

| Item | Result |
|---|---|
| Worker state | IDLE |
| Visible scaffold | SCAFFOLD_READY |
| Latest report | REPORTS/latest_report.md |
""",
            encoding="utf-8",
        )
        (root / "STATUS.md").write_text("Status: `IDLE`\n", encoding="utf-8")
        (root / "RUN_LOG.md").write_text("## log\n", encoding="utf-8")
        (root / "DECISION_REQUIRED.md").write_text(
            "## Open Decisions\n\nNo current user action required for normal safe GitHub status-file supervision.\n",
            encoding="utf-8",
        )
        (root / "QUANT_SYSTEM_TARGETS.md").write_text(
            "# Targets\n\n## 1. North star\n\nBuild simulation-only review flow.\n",
            encoding="utf-8",
        )
        (root / "REPORTS" / "latest_report.md").write_text(
            """# Latest Report

Conclusion line for a report.

## Summary

- Contracts after scan: 7
- Spread candidates: 4
""",
            encoding="utf-8",
        )
        (root / "REPORTS" / "quant_system_gap_report.md").write_text(
            """# Quant System Gap Report

结论：fixture replay works but is not a statistical conclusion.

## Can It Answer The Key Question?

Only fixture-level replay is available.

## Remaining Gaps

- Larger safe samples.
- Parameter sensitivity.

## Next Three Safe Codex Tasks

1. TASK-011: Add parameter sensitivity report.
2. TASK-012: Extend dashboard tables.
3. TASK-013: Add repository-local fill-event fixture.
""",
            encoding="utf-8",
        )
        return root

    def test_writes_packet_and_review_block(self):
        root = self.make_root()

        context = prepare_model_review_packet.build_context(root)
        prepare_model_review_packet.write_outputs(root, context)

        packet = (root / "GPT_REVIEW_PACKET.md").read_text(encoding="utf-8")
        review = (root / "GPT_REVIEW.md").read_text(encoding="utf-8")
        self.assertIn("## Current State", packet)
        self.assertIn("## Next Three Safe Repository Tasks", packet)
        self.assertIn("Add parameter sensitivity report.", packet)
        self.assertNotIn("TASK-011:", packet)
        self.assertIn("<!-- model-review-packet:start -->", review)
        ok, errors = prepare_model_review_packet.check_outputs(root)
        self.assertTrue(ok, errors)

    def test_redacts_private_paths_and_credentials(self):
        text = "/Users/example/secret api_key = abc123 ghp_abcdefghijkl"
        redacted = prepare_model_review_packet.redact(text)
        self.assertNotIn("/Users/example", redacted)
        self.assertNotIn("abc123", redacted)
        self.assertNotIn("ghp_abcdefghijkl", redacted)


if __name__ == "__main__":
    unittest.main()
