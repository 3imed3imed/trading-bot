"""Deterministic, cost-inclusive performance statistics for locked OOS and paper trades."""
from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Trade:
    return_fraction: float
    position_fraction: float = 1.0


def _max_drawdown(equity: list[float]) -> float:
    peak = equity[0]
    worst = 0.0
    for value in equity:
        peak = max(peak, value)
        worst = max(worst, (peak - value) / peak if peak else 0.0)
    return worst


def bootstrap_expectancy_ci(values: list[float], confidence: float = 0.95, samples: int = 2000, seed: int = 7) -> tuple[float | None, float | None]:
    if len(values) < 2:
        return None, None
    rng = random.Random(seed)
    means = sorted(statistics.fmean(rng.choices(values, k=len(values))) for _ in range(samples))
    alpha = (1.0 - confidence) / 2.0
    lo = means[max(0, int(alpha * samples))]
    hi = means[min(samples - 1, int((1.0 - alpha) * samples) - 1)]
    return lo, hi


def summarize(trades: Iterable[Trade], starting_equity: float = 100.0, minimum_sample: int = 500) -> dict[str, float | int | str | None]:
    rows = list(trades)
    returns = [t.return_fraction for t in rows]
    wins = [x for x in returns if x > 0]
    losses = [x for x in returns if x < 0]
    equity = [starting_equity]
    for trade in rows:
        if not 0 <= trade.position_fraction <= 1:
            raise ValueError("position_fraction must be between 0 and 1")
        equity.append(equity[-1] * (1 + trade.return_fraction * trade.position_fraction))
    gross_win = sum(wins)
    gross_loss = abs(sum(losses))
    ci_low, ci_high = bootstrap_expectancy_ci(returns)
    count = len(rows)
    return {
        "status": "VALID" if count >= minimum_sample and ci_low is not None and ci_low > 0 else "INSUFFICIENT_OR_UNPROVEN",
        "trade_count": count,
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": len(wins) / count if count else None,
        "average_win": statistics.fmean(wins) if wins else None,
        "average_loss": statistics.fmean(losses) if losses else None,
        "expectancy_per_trade": statistics.fmean(returns) if returns else None,
        "expectancy_ci_low": ci_low,
        "expectancy_ci_high": ci_high,
        "profit_factor": gross_win / gross_loss if gross_loss else (math.inf if gross_win else None),
        "starting_equity": starting_equity,
        "ending_equity": equity[-1],
        "net_profit": equity[-1] - starting_equity,
        "return_fraction": equity[-1] / starting_equity - 1 if starting_equity else None,
        "maximum_drawdown": _max_drawdown(equity),
    }
