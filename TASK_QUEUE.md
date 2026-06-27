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
- Status: superseded
- Type: worker_stability
- Title: 稳定 Codex worker 定时扫描闭环
- Request: Original task was too broad and the safety scanner stopped it.
- Expected output: superseded by TASK-004A.
- Safety: not_applicable
- Created: 2026-06-27
- Last update: rewritten by ChatGPT
- Result: superseded by safer scoped task

### TASK-004A
- Status: pending
- Type: worker_stability_status_only
- Title: 稳定本地 worker 的状态扫描与回写
- Request: 只在当前 GitHub 仓库内做状态类维护。请检查并改进 Mac mini 本地 worker 的定时扫描闭环：把扫描间隔从 300 秒改为 60 秒；每 60 秒拉取仓库、读取 TASK_QUEUE.md、执行第一个安全任务、更新 STATUS.md/RUN_LOG.md/REPORTS/DECISION_REQUIRED.md，并把状态文件推送回 liyuanqiang-spec/-。增加防重复运行锁、单轮超时、普通失败重试三轮、logs/worker.log 记录、scripts/check_worker_health.sh 健康检查、heartbeat 心跳记录、dry-run 验证。完成后连续验证至少 3 轮“读取—执行—回写—推送”闭环，并在 STATUS.md 写入稳定性报告。
- Expected output: updated worker scripts, launchd interval set to 60 seconds, scripts/check_worker_health.sh, heartbeat evidence, STATUS.md stability report, RUN_LOG.md logs.
- Safety: status_only_repo_maintenance
- Created: 2026-06-27
- Last update: interval changed to 60 seconds by ChatGPT
- Result: pending worker execution

### TASK-005
- Status: pending
- Type: dashboard
- Title: 创建可视化查看入口
- Request: 在 TASK-004A 完成后，创建一个简单、可直接在 GitHub 页面查看的 `WORKER_DASHBOARD.md`，用于用户打开仓库页面即可看见 Codex 是否在工作。Dashboard 至少包含：最后心跳时间、worker 状态、当前任务、最近完成任务、最近失败任务、最近报告链接、最近一次 push/commit、是否有 DECISION_REQUIRED 阻塞、当前安全模式、下一步建议。每次 worker 扫描结束后自动更新该文件。同步在 README.md 顶部增加“查看工作状态”的入口链接，指向 `WORKER_DASHBOARD.md`。
- Expected output: `WORKER_DASHBOARD.md` and README entry; future worker runs update dashboard automatically.
- Safety: status_and_report_only
- Created: 2026-06-27
- Last update: updated by ChatGPT
- Result: pending worker execution
