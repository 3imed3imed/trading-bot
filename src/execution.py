"""Conservative execution feasibility shared by backtest and paper modes."""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class Quote:
    bid: float
    ask: float
    bid_size: int
    ask_size: int
    timestamp_age_seconds: float

@dataclass(frozen=True)
class FillEstimate:
    feasible: bool
    reason: str
    reference_mid: float | None
    estimated_price: float | None
    spread_bps: float | None
    slippage_bps: float | None


def estimate_market_buy(quote: Quote, quantity: int, minute_volume: int, maximum_participation: float = 0.02, stale_after_seconds: float = 5.0) -> FillEstimate:
    if quantity <= 0:
        return FillEstimate(False, "quantity must be positive", None, None, None, None)
    if quote.bid <= 0 or quote.ask <= quote.bid:
        return FillEstimate(False, "invalid or locked/crossed quote", None, None, None, None)
    if quote.timestamp_age_seconds > stale_after_seconds:
        return FillEstimate(False, "quote is stale", None, None, None, None)
    if minute_volume <= 0 or quantity > minute_volume * maximum_participation:
        return FillEstimate(False, "participation limit exceeded", None, None, None, None)
    if quantity > quote.ask_size:
        return FillEstimate(False, "displayed ask size cannot support conservative fill", None, None, None, None)
    mid = (quote.bid + quote.ask) / 2
    spread_bps = (quote.ask - quote.bid) / mid * 10_000
    participation = quantity / minute_volume
    impact_bps = spread_bps * (participation / maximum_participation) ** 0.5
    estimated = quote.ask * (1 + impact_bps / 10_000)
    total_slippage = (estimated - mid) / mid * 10_000
    return FillEstimate(True, "capacity and quote checks passed", mid, estimated, spread_bps, total_slippage)
