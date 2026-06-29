import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "render_supervisor_conversation.py"


def load_module():
    spec = importlib.util.spec_from_file_location("render_supervisor_conversation", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SupervisorConversationTest(unittest.TestCase):
    def test_renders_dialogue_and_redacts_secrets(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "TASK_QUEUE.md").write_text(
                """# TASK_QUEUE

### TASK-001
- Status: completed
- Type: handshake
- Title: Verify loop
- Request: Run safe status check with api_key=sk-test1234567890
- Result: worker reported back
""",
                encoding="utf-8",
            )
            (root / "GPT_VISIBLE_STATUS.md").write_text(
                "- Status: `IDLE`\n- Worker mode: `IDLE`\n",
                encoding="utf-8",
            )
            (root / "RUN_LOG.md").write_text(
                "## 2026-06-29 12:00:00 +0800\n\n"
                "- Event: gpt_handshake\n"
                "- Detail: Task TASK-001 completed\n",
                encoding="utf-8",
            )

            rendered = module.render(root)

        self.assertIn("GPT -> Codex: TASK-001", rendered)
        self.assertIn("Codex -> GPT: TASK-001", rendered)
        self.assertIn("worker reported back", rendered)
        self.assertNotIn("sk-test1234567890", rendered)
        self.assertIn("api_key=***", rendered)


if __name__ == "__main__":
    unittest.main()
