import importlib.util
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "send_default_mail.py"


def load_module():
    spec = importlib.util.spec_from_file_location("send_default_mail", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SendDefaultMailTest(unittest.TestCase):
    def test_dry_run_does_not_print_recipient(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            recipient_file = Path(tmp) / "recipient.txt"
            recipient_file.write_text("person@example.com\n", encoding="utf-8")
            output = StringIO()
            with redirect_stdout(output):
                code = module.main(
                    [
                        "--subject",
                        "test",
                        "--body",
                        "hello",
                        "--recipient-file",
                        str(recipient_file),
                        "--dry-run",
                    ]
                )
        self.assertEqual(code, 0)
        self.assertIn("LOCAL_DEFAULT_MAIL_DRY_RUN_OK", output.getvalue())
        self.assertNotIn("person@example.com", output.getvalue())

    def test_missing_recipient_is_reported_without_value(self):
        module = load_module()
        output = StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            with redirect_stdout(output):
                code = module.main(
                    [
                        "--subject",
                        "test",
                        "--body",
                        "hello",
                        "--recipient-file",
                        str(Path(tmp) / "missing.txt"),
                        "--dry-run",
                    ]
                )
        self.assertEqual(code, 2)
        self.assertEqual(output.getvalue().strip(), "LOCAL_DEFAULT_MAIL_MISSING")


if __name__ == "__main__":
    unittest.main()
