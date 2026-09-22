# TASK-034: Mac mini health check and local model deployment

- Created: 2026-09-22 (Asia/Shanghai, UTC+08:00)
- Requested by: owner in ChatGPT; direct execution requested, not another tutorial or handoff document.
- Target: the owner's actual local Mac mini, not a cloud runner or ChatGPT container.
- Goal: inspect the computer, install LM Studio if compatible and permitted, download exactly one model, run an initial text-only test, and return measured results.
- Model: `lmstudio-community/Qwen3.5-4B-MLX-4bit`.
- Phase: `PHASE_1_SIMULATION_ONLY`; no training, distillation, multi-model setup, or trading in this task.

## 1. Establish real local execution and acknowledge pickup

Read the existing project instructions and `RISK_CONTROL.md`. Keep all existing approval and sandbox requirements in force. Confirm the execution environment is the owner's local Apple Silicon macOS host. Do not treat a cloud VM, repository checkout, or successful download elsewhere as installation on the Mac mini.

On actual pickup, mark this task running and publish a sanitized acknowledgement with marker `LOCAL_LLM_TASK_PICKED_UP_20260922`. Do not claim pickup or execution until it actually occurred.

## 2. Read-only preflight

Measure, rather than assume:
- macOS version and CPU architecture/chip family;
- physical memory, currently available memory and memory pressure;
- free disk capacity in the proposed download/model locations;
- whether LM Studio is installed, its version, whether its CLI is available, and whether another instance is running;
- network reachability to the official download/model sources without changing proxy or VPN configuration.

Do not collect or publish hardware serial numbers, UUIDs, device names, user names, private absolute paths, IP addresses, account details, environment dumps, credentials, tokens, or unrelated files. Report the host simply as `local Mac mini` and redact paths to `~` or project-relative form.

The verified LM Studio requirements page states Apple Silicon and macOS 14 or newer, with 16GB+ RAM recommended; 8GB systems may work with smaller models and modest context. Do not assume the owner's RAM is 16GB or any other amount. Confirm current requirements at execution time. Do not upgrade macOS automatically. Assess the actual model download and temporary-storage needs; retain reasonable free-space headroom. Do not delete existing files to make room.

## 3. Install only the requested application and model

Verified source pages (recheck version/availability before downloading):
- https://lmstudio.ai/download
- https://lmstudio.ai/docs/app/system-requirements
- https://lmstudio.ai/models/qwen/qwen3.5-4b
- https://huggingface.co/lmstudio-community/Qwen3.5-4B-MLX-4bit

Use the official signed Apple Silicon LM Studio release and the exact MLX 4bit model repository above. Resolve the actual download URL from official pages; do not invent versioned URLs. Check publisher/signature and available integrity information. Record application version and model revision. Do not execute arbitrary downloaded shell installers or model-supplied code.

Reuse an existing compatible LM Studio installation and an already-downloaded identical model. Do not replace or disturb another user's running application. Install to a user-scoped application directory only where allowed by the current local permission boundary. The owner has requested installation, but this task does NOT bypass `RISK_CONTROL.md`, change sandbox settings, or grant additional operating-system privileges. If the current `workspace-write` sandbox prevents installing outside the project or downloading required files, report the exact permission needed and request it through the normal local approval interface. Stop that step if approval cannot be obtained. Do not weaken guards, disable Gatekeeper, change firewall/VPN, use privileged shortcuts, or modify system security settings.

Keep all model weights, installers, caches, and raw measurements LOCAL and out of Git. Use an existing safe model directory or a clearly isolated locally excluded directory permitted by the runtime. Verify ignore/exclude coverage before any download inside the repository. Never commit binaries, weights, private machine data, or screenshots of unrelated windows. Do not create a second quant strategy database or modify the existing quant system.

Only install LM Studio and this one model. No Ollama, Docker, unrelated agents, cloud inference, paid services, or background autostart setup. Do not switch to another model silently. If the exact model/runtime is unsupported, stop with a specific compatibility finding.

## 4. Configure and actually test

- One model loaded; text input only.
- Start with 4096 context and a modest maximum output (about 512 tokens); lower context if measured memory pressure requires it.
- Disable `Enable Thinking` for the initial experience, if this control is available in the installed runtime; report the actual setting rather than inventing a field name.
- Do not enable external tools, remote computer control, public endpoints, or network access for the small model.
- If a local API is needed for testing, bind only to loopback, check for port conflicts, and stop the temporary server after testing unless it was already running.

Save a local preset with this system prompt:

> 你是我的量化策略整理员。将输入资料整理成：交易标的、选取指标、买入条件、卖出条件、调仓周期、缺失信息。原文没有的内容必须写“未提供”，不得补造收益或交易规则。

Run these synthetic, non-private checks:
1. Basic Chinese interaction: ask it to explain in two sentences the difference between a model and an agent. Record its actual response.
2. Strategy extraction using the preset: input `只交易流动性达标的股票ETF；每月末按过去20个交易日收益率选前3只，等权持有；下月末重新筛选。` Verify that it does not invent a liquidity threshold, execution price/time, transaction costs, stop loss, historical return, or other missing rules.
3. Missing-information check: ask `这套策略过去五年的年化收益是多少？` without supplying performance data; verify that the answer acknowledges the missing evidence instead of fabricating a number.

Record cold-load duration separately from generation latency, measured output speed when exposed by the runtime, and memory pressure before/during/after. If metrics are unavailable, explicitly say unmeasured. These checks validate deployment and basic behavior, not profitability or model competence for live investing. Capture only the LM Studio test window when screenshot permission exists; otherwise provide sanitized command/API output and state that no screenshot was captured.

## 5. Evidence and completion states

Write a sanitized Chinese report at `REPORTS/local_lmstudio_qwen35_20260922.md` with:
- actual chip family, RAM, macOS, free disk, and preflight verdict;
- install/download status, application version, exact model ID and revision;
- settings actually applied;
- actual test inputs/outputs and measurements;
- clear completed/failed/not-attempted status for each step;
- at most one concrete required user action if blocked.

Keep detailed private logs local; commit only the sanitized report and normal repository status updates. Update `TASK_QUEUE.md`, `STATUS.md`, `RUN_LOG.md`, and `GPT_VISIBLE_STATUS.md` consistently with actual evidence. Preserve prior history and unrelated tasks.

Use one accurate final marker:
- `LOCAL_LLM_READY_20260922`: application starts, exact model loads, and real local tests ran; report test failures even if deployment works.
- `LOCAL_LLM_PREFLIGHT_ONLY_20260922`: computer inspection completed but installation/testing did not.
- `LOCAL_LLM_APPROVAL_REQUIRED_20260922`: a named local permission blocks a step.
- `LOCAL_LLM_NETWORK_BLOCKED_20260922`: official download/model access failed.
- `LOCAL_LLM_INCOMPATIBLE_20260922`: verified hardware/OS/runtime incompatibility.
- `LOCAL_LLM_SETUP_FAILED_20260922`: another precise failure, with sanitized evidence.

A queued task, a generated script, a downloaded installer, or an empty report is NOT a successful installation. Do not mark the goal achieved without actual execution evidence. Do not retry indefinitely.

## Hard stops

No live trading, broker connection, order placement/cancellation, funds or margin movement, secret exposure, original-data deletion, or `danger-full-access`. No modifications to existing quant services, risk gates, remote access, or computer-wide settings. This task does not authorize any broader permissions or replacement of original files.
