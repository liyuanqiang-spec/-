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
- Status: pending
- Type: data_schema
- Title: 数据字段标准化
- Request: 定义期权日线、Tick、盘口、成交、持仓、保证金、手续费字段；输出 DATA_SCHEMA.md。
- Expected output: DATA_SCHEMA.md
- Safety: data_only
- Created: 2026-06-27
- Last update:
- Result:

### TASK-003
- Status: pending
- Type: research
- Title: 低流动性合约扫描
- Request: 扫描不活跃但有持仓的合约；输出候选合约列表；输出筛选理由。
- Expected output: REPORTS/low_liquidity_candidates.md
- Safety: data_and_report_only
- Created: 2026-06-27
- Last update:
- Result:
