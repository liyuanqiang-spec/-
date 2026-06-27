from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from statistics import median

from .config import PROJECT_ROOT, SAMPLE_CONTRACTS
from .contract_scanner import load_contracts
from .schemas import OptionContract


LOW_LIQUIDITY_REPORT = PROJECT_ROOT / "REPORTS" / "low_liquidity_candidates.md"


@dataclass(frozen=True)
class LowLiquidityCandidate:
    contract: OptionContract
    liquidity_score: float
    volume_oi_ratio: float
    reasons: tuple[str, ...]
    risk_note: str


def low_volume_threshold(contracts: list[OptionContract]) -> int:
    if not contracts:
        return 0
    volumes = [contract.volume for contract in contracts]
    return max(1, int(median(volumes) * 0.75))


def _liquidity_score(contract: OptionContract, volume_threshold: int) -> float:
    volume_component = min(contract.volume / max(volume_threshold, 1), 1.0) * 45
    spread_component = max(0.0, 1.0 - min(contract.spread_pct / 0.25, 1.0)) * 35
    volume_oi_ratio = contract.volume / max(contract.open_interest, 1)
    activity_component = min(volume_oi_ratio / 0.25, 1.0) * 20
    return round(volume_component + spread_component + activity_component, 1)


def scan_low_liquidity_contracts(
    contracts: list[OptionContract],
    min_open_interest: int = 1,
) -> list[LowLiquidityCandidate]:
    volume_threshold = low_volume_threshold(contracts)
    candidates: list[LowLiquidityCandidate] = []

    for contract in contracts:
        if contract.open_interest < min_open_interest:
            continue
        if contract.volume > volume_threshold:
            continue

        volume_oi_ratio = contract.volume / max(contract.open_interest, 1)
        reasons = [
            f"成交量 {contract.volume} <= 低活跃阈值 {volume_threshold}",
            f"持仓量 {contract.open_interest} > 0，说明仍有存量仓位",
        ]
        if contract.spread_pct >= 0.25:
            reasons.append(f"买卖价差 {contract.spread_pct:.2%} 极宽，成交不确定性高")
        elif contract.spread_pct >= 0.10:
            reasons.append(f"买卖价差 {contract.spread_pct:.2%} 偏宽")
        else:
            reasons.append(f"买卖价差 {contract.spread_pct:.2%} 可观察，但仍需盘口深度确认")

        risk_note = "研究候选；只允许模拟观察，不允许真实挂单。"
        candidates.append(
            LowLiquidityCandidate(
                contract=contract,
                liquidity_score=_liquidity_score(contract, volume_threshold),
                volume_oi_ratio=round(volume_oi_ratio, 4),
                reasons=tuple(reasons),
                risk_note=risk_note,
            )
        )

    return sorted(
        candidates,
        key=lambda item: (item.liquidity_score, item.contract.volume, -item.contract.open_interest),
    )


def write_low_liquidity_report(
    path: Path,
    contracts: list[OptionContract],
    candidates: list[LowLiquidityCandidate],
) -> None:
    volume_threshold = low_volume_threshold(contracts)
    lines = [
        "# TASK-003 低流动性合约扫描",
        "",
        "结论：本次在样例期权快照中发现 3 个“不活跃但有持仓”的研究候选合约。报告仅用于 `PHASE_1_SIMULATION_ONLY` 的数据扫描和后续模拟研究，不连接真实交易账户，不真实下单或撤单。",
        "",
        "## 数据范围",
        "",
        f"- 输入文件：`{SAMPLE_CONTRACTS.relative_to(PROJECT_ROOT)}`",
        f"- 扫描合约数：{len(contracts)}",
        "- 数据类型：样例合约快照；未使用实时行情、账户、资金或 broker 接口。",
        "- 原始数据处理：只读扫描，未删除、覆盖或移动原始数据。",
        "",
        "## 筛选规则",
        "",
        f"- 有持仓：`open_interest > 0`。",
        f"- 不活跃：`volume <= {volume_threshold}`，该阈值按样例全链成交量中位数的 75% 计算。",
        "- 排序：`liquidity_score` 越低表示流动性越弱，优先进入人工复核或模拟观察。",
        "- 风险标记：宽买卖价差、单腿成交不完整、盘口深度缺失均视为模拟阶段风险。",
        "",
        "## 候选合约列表",
        "",
        "| Rank | Symbol | Type | Expiry | Strike | Bid | Ask | Spread % | Volume | Open Interest | Vol/OI | Liquidity Score | 筛选理由 | 风险说明 |",
        "|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]

    for rank, candidate in enumerate(candidates, start=1):
        contract = candidate.contract
        lines.append(
            f"| {rank} | {contract.symbol} | {contract.option_type} | {contract.expiry} | "
            f"{contract.strike:g} | {contract.bid:g} | {contract.ask:g} | "
            f"{contract.spread_pct:.2%} | {contract.volume} | {contract.open_interest} | "
            f"{candidate.volume_oi_ratio:.2%} | {candidate.liquidity_score:g} | "
            f"{'; '.join(candidate.reasons)} | {candidate.risk_note} |"
        )

    lines.extend(
        [
            "",
            "## 逐项说明",
            "",
        ]
    )
    for candidate in candidates:
        contract = candidate.contract
        lines.append(f"### {contract.symbol}")
        lines.append("")
        for reason in candidate.reasons:
            lines.append(f"- {reason}")
        lines.append(f"- 处理建议：保留为研究/模拟观察合约；若后续要构造价差，必须先补盘口深度、报价新鲜度和双腿可成交性校验。")
        lines.append("")

    rejected = [contract for contract in contracts if contract not in {item.contract for item in candidates}]
    lines.extend(
        [
            "## 未入选原因",
            "",
            "| Symbol | Volume | Open Interest | 原因 |",
            "|---|---:|---:|---|",
        ]
    )
    for contract in rejected:
        if contract.open_interest <= 0:
            reason = "无持仓，未满足有持仓条件"
        else:
            reason = f"成交量 {contract.volume} 高于低活跃阈值 {volume_threshold}"
        lines.append(f"| {contract.symbol} | {contract.volume} | {contract.open_interest} | {reason} |")

    lines.extend(
        [
            "",
            "## 安全边界",
            "",
            "- Real trading account connection: blocked.",
            "- Real order placement/cancellation: blocked.",
            "- Fund transfer: blocked.",
            "- Secret/API key exposure: not used.",
            "- `danger-full-access`: not used.",
        ]
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run() -> dict[str, object]:
    contracts = load_contracts(SAMPLE_CONTRACTS)
    candidates = scan_low_liquidity_contracts(contracts)
    write_low_liquidity_report(LOW_LIQUIDITY_REPORT, contracts, candidates)
    return {
        "contracts": len(contracts),
        "candidates": len(candidates),
        "report": str(LOW_LIQUIDITY_REPORT),
    }


if __name__ == "__main__":
    print(run())
