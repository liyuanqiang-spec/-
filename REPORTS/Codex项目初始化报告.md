# Codex 项目初始化报告

日期：2026-06-27

结论：项目初始化已完成，当前处于 `SIMULATION_ONLY`。已经具备离线样例数据、合约扫描、价差计算、简单回测、风控检查和报告生成能力；真实交易、真实下单和资金操作仍被硬性禁止。

## 1. 工具和插件状态

| 项目 | 状态 | 说明 |
|---|---:|---|
| GitHub | 可用但未登录 | GitHub 插件可用，`gh` 需要 `gh auth login` |
| OpenAI Developers | 已连通 | 可见 Personal 组织和 Default project |
| Browser / Chrome | 可用 | 本机已缓存 Browser/Chrome 插件 |
| Google Drive | 已连通 | 账号可访问 |
| Google Sheets | 已连通 | 通过 Google Drive 插件操作 |
| Vercel / Sites | CLI 已安装 | `vercel` 可用，部署前需要登录 |
| Supabase | CLI 已安装 | Homebrew 版 `supabase` 可用，登录或 token 待配置 |
| Codex Security | 可用 | `security-best-practices`、`bandit`、`pip-audit` 已准备 |
| Figma | 已连通 | 当前账号为 View seat |
| Hugging Face | CLI 已安装 | `hf` 可用，账号未登录 |

## 2. 已创建 Skills

项目级 Skills 已放在 `.codex/skills/`：

- `quant-research`
- `market-data`
- `options-backtest`
- `liquidity-spread`
- `risk-control`
- `report-writer`
- `code-review`
- `deployment`
- `trading-safety`
- `project-manager`

## 3. 已创建根目录文件

- `AGENTS.md`
- `README.md`
- `PROJECT_PLAN.md`
- `TASKS.md`
- `STATUS.md`
- `CHANGELOG.md`
- `RISK_CONTROL.md`

## 4. 已建立工作规则

- 所有开发任务先写计划，再执行。
- 每完成一个阶段，更新 `STATUS.md`。
- 遇到报错先自动修复三轮。
- 需要用户决策时只给 A/B/C 三个方案，并标明推荐方案。
- 真实交易、真实下单、资金划转、删除重要数据前必须停止并等待确认。
- 当前只允许数据下载、清洗、回测、模拟交易准备、报告生成。

## 5. 最小可运行系统

已建立：

- 数据目录：`data/raw/`、`data/clean/`、`data/contracts/`、`data/backtests/`、`reports/`
- 样例数据：`data/contracts/sample_options.csv`
- 合约扫描模块：`src/codex_quant/contract_scanner.py`
- 价差计算模块：`src/codex_quant/spread_calculator.py`
- 简单回测模块：`src/codex_quant/backtester.py`
- 风控检查模块：`src/codex_quant/risk_control.py`
- 结果报告模块：`src/codex_quant/report_writer.py`
- 管线入口：`src/codex_quant/run_pipeline.py`

## 6. 验证结果

| 验证 | 结果 |
|---|---:|
| 样例管线 | 通过：7 个合约，4 个价差候选 |
| 单元测试 | 通过：1 个测试 |
| Python 编译检查 | 通过 |
| Bandit 安全扫描 | 通过 |

生成报告：

- `reports/latest_report.md`

## 7. 当前问题

- GitHub、Vercel、Supabase、Hugging Face 账号授权尚未完成。
- Figma 当前是 View seat，写入设计可能受权限限制。
- 还没有选定真实市场数据源。
- 样例数据量很小，报告中的 `LOW_SAMPLE` 是预期提示。

## 8. 下一步建议

推荐先做 A：

A. 配置真实市场数据源，只做下载、清洗、回测，不触碰交易权限。  
B. 先完成 GitHub/Vercel/Supabase/Hugging Face 登录授权。  
C. 先扩展单元测试和风控测试，再接数据。

是否需要你确认：需要。下一步如果要接真实数据源或登录云服务，需要你确认账号授权方式；不涉及真实交易。
