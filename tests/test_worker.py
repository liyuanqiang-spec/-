import unittest

from src.codex_quant.worker import blocked_reason, parse_task_queue


class WorkerTest(unittest.TestCase):
    def test_parse_pending_task(self):
        text = """# TASK_QUEUE

### TQ-1
- Status: pending
- Type: pipeline
- Request: Run sample pipeline.
"""
        tasks = parse_task_queue(text)

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_id, "TQ-1")
        self.assertEqual(tasks[0].status, "pending")
        self.assertEqual(tasks[0].task_type, "pipeline")

    def test_blocks_real_trading_request(self):
        task = parse_task_queue(
            """### TQ-2
- Status: pending
- Type: pipeline
- Request: 真实下单一手白银期货
"""
        )[0]

        self.assertIn("real order", blocked_reason(task))


if __name__ == "__main__":
    unittest.main()
