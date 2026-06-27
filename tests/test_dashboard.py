import tempfile
import unittest
from pathlib import Path

from src.codex_quant.dashboard import build_dashboard, parse_queue_tasks


class DashboardTest(unittest.TestCase):
    def test_parse_queue_tasks(self):
        tasks = parse_queue_tasks(
            """# TASK_QUEUE

### TASK-005
- Status: running
- Type: dashboard
- Title: 创建可视化查看入口
- Request: Create dashboard.
- Result: worker started
"""
        )

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_id, "TASK-005")
        self.assertEqual(tasks[0].status, "running")
        self.assertEqual(tasks[0].title, "创建可视化查看入口")

    def test_build_dashboard_contains_required_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "TASK_QUEUE.md").write_text(
                """# TASK_QUEUE

### TASK-005
- Status: completed
- Type: dashboard
- Title: Dashboard
- Result: dashboard generated
""",
                encoding="utf-8",
            )
            (root / "STATUS.md").write_text("Status: `TASK_005_COMPLETED`\n", encoding="utf-8")
            (root / "RUN_LOG.md").write_text("", encoding="utf-8")
            (root / "DECISION_REQUIRED.md").write_text("# DECISION_REQUIRED.md\n", encoding="utf-8")
            reports = root / "reports"
            reports.mkdir()
            (reports / "latest_report.md").write_text("# report\n", encoding="utf-8")

            dashboard = build_dashboard(root)

        self.assertIn("Last heartbeat time", dashboard)
        self.assertIn("Worker status", dashboard)
        self.assertIn("TASK-005", dashboard)
        self.assertIn("PHASE_1_SIMULATION_ONLY", dashboard)


if __name__ == "__main__":
    unittest.main()
