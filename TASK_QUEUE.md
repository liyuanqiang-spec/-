# TASK_QUEUE.md

This queue is the GitHub handoff channel from ChatGPT to Codex.

Worker rule: execute the first task whose status is `pending` and whose type is safe. If a task touches real trading, money, original-data deletion, secrets, or `danger-full-access`, stop and write `DECISION_REQUIRED.md`.

## Tasks

### TASK-000-GPT-HANDSHAKE
- Status: completed
- Type: status_check
- Title: GPT 到 Codex 握手测试
- Request: 验证 ChatGPT/GitHub -> Mac mini Codex worker -> STATUS/RUN_LOG -> GitHub 的闭环。
- Expected output: STATUS.md and RUN_LOG.md record GPT_HANDSHAKE_OK.
- Safety: status_only
- Created: 2026-06-27
- Last update: updated by worker
- Result: GPT handshake completed by local worker

### TASK-001
- Status: completed
- Type: development
- Title: 白银期权价差策略 MVP 初始化
- Request: 建立项目结构；建立期权合约扫描模块框架；建立价差计算模块框架；建立简单回测模块框架；建立报告输出模块框架；建立风险控制检查模块；不接实盘，不真实下单。
- Expected output: runnable MVP scaffold and updated status/report files.
- Safety: simulation_only
- Created: 2026-06-27
- Last update: updated by worker
- Result: codex exec completed

### TASK-002
- Status: completed
- Type: data_schema
- Title: 数据字段标准化
- Request: 定义期权日线、Tick、盘口、成交、持仓、保证金、手续费字段；输出 DATA_SCHEMA.md。
- Expected output: DATA_SCHEMA.md
- Safety: data_only
- Created: 2026-06-27
- Last update: updated by worker
- Result: codex exec completed

### TASK-003
- Status: completed
- Type: research
- Title: 低流动性合约扫描
- Request: 扫描不活跃但有持仓的合约；输出候选合约列表；输出筛选理由。
- Expected output: REPORTS/low_liquidity_candidates.md
- Safety: data_and_report_only
- Created: 2026-06-27
- Last update: updated by worker
- Result: codex exec completed

### TASK-004
- Status: pending
- Type: worker_stability
- Title: 稳定 Codex worker 定时扫描闭环
- Request: 暂停 GitHub Actions + OpenAI API 的 GPT 主管自动化，不要新增复杂云端主管；当前第一目标是把 Mac mini 本地 Codex worker 做稳定。请检查并强化 worker 的定时扫描能力，确保它每 300 秒自动 pull GitHub、读取 TASK_QUEUE.md、执行第一个安全任务、更新 STATUS.md/RUN_LOG.md/REPORTS/DECISION_REQUIRED.md，并能 git add/commit/push 回 liyuanqiang-spec/-。同时增加防重复运行锁、超时控制、失败自动重试三轮、日志写入 logs/worker.log、健康检查脚本 scripts/check_worker_health.sh、heartbeat 心跳任务和 dry-run 验证。完成后连续验证至少 3 轮定时扫描，确认“任务读取—执行—回写—推送”闭环稳定，再把结果写入 STATUS.md；若权限、git、launchd、邮件或网络有问题就写入 DECISION_REQUIRED.md。
- Expected output: updated worker scripts, scripts/check_worker_health.sh, heartbeat evidence, STATUS.md stability report, RUN_LOG.md logs, and no unresolved DECISION_REQUIRED.md blocker unless an actual authorization problem exists.
- Safety: PHASE_1_SIMULATION_ONLY
- Hard stops: real trading, real order placement, real order cancellation, fund transfer, original-data deletion, secret exposure, danger-full-access, system-level destructive change, large paid API/cloud calls.
- Created: 2026-06-27
- Last update: created by ChatGPT
- Result: pending worker execution
