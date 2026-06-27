from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _preferred_dir(primary: str, fallback: str) -> Path:
    primary_path = PROJECT_ROOT / primary
    fallback_path = PROJECT_ROOT / fallback
    return primary_path if primary_path.exists() else fallback_path


DATA_DIR = _preferred_dir("DATA", "data")
CONTRACTS_DIR = DATA_DIR / "contracts"
REPORTS_DIR = _preferred_dir("REPORTS", "reports")
SAMPLE_CONTRACTS = CONTRACTS_DIR / "sample_options.csv"
LATEST_REPORT = REPORTS_DIR / "latest_report.md"
TASK_QUEUE = PROJECT_ROOT / "TASK_QUEUE.md"
STATUS_FILE = PROJECT_ROOT / "STATUS.md"
RUN_LOG = PROJECT_ROOT / "RUN_LOG.md"
DECISION_REQUIRED = PROJECT_ROOT / "DECISION_REQUIRED.md"
WORKER_DASHBOARD = PROJECT_ROOT / "WORKER_DASHBOARD.md"
WORKER_PID = PROJECT_ROOT / ".codex_worker.pid"
WORKER_OUTPUT = PROJECT_ROOT / ".codex_worker.out"

DEFAULT_MIN_VOLUME = 30
DEFAULT_MAX_SPREAD_PCT = 0.25
TRADING_MODE = "SIMULATION_ONLY"
