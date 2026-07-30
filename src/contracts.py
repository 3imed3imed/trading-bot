"""Stable contracts shared by discovery, event backtest, paper and live modes."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Mapping

class Mode(str, Enum):
    DISCOVERY = "DISCOVERY"
    LOCKED_EVENT_BACKTEST = "LOCKED_EVENT_BACKTEST"
    PAPER = "PAPER"
    LIVE = "LIVE"

class Status(str, Enum):
    PASS = "PASS"
    REJECTED = "REJECTED"
    BLOCKED = "BLOCKED"

@dataclass(frozen=True)
class DataEnvelope:
    event_time: datetime
    known_time: datetime
    ingested_at: datetime
    source: str
    content_hash: str
    payload: Mapping[str, Any]

    def validate_for_decision(self, decision_time: datetime) -> None:
        if self.known_time > decision_time:
            raise ValueError("future information: known_time exceeds decision_time")
        if self.event_time > self.known_time:
            raise ValueError("event_time cannot follow known_time")
        if self.known_time > self.ingested_at:
            raise ValueError("known_time cannot follow ingested_at")
        if not self.source or not self.content_hash:
            raise ValueError("source and content_hash are mandatory")

@dataclass(frozen=True)
class Signal:
    strategy_id: str
    symbol: str
    decision_time: datetime
    direction: int
    confidence: float
    evidence_hashes: tuple[str, ...]
    invalidation: str

    def __post_init__(self) -> None:
        if self.direction not in (-1, 0, 1):
            raise ValueError("direction must be -1, 0 or 1")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        if not self.evidence_hashes:
            raise ValueError("a signal requires immutable evidence")
        if not self.invalidation:
            raise ValueError("a signal requires an invalidation condition")

@dataclass(frozen=True)
class OrderIntent:
    signal: Signal
    quantity: int
    limit_price: float | None
    maximum_participation: float
    maximum_slippage_bps: float

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        if not 0 < self.maximum_participation <= 0.10:
            raise ValueError("participation must be in (0, 10%]")
        if self.maximum_slippage_bps < 0:
            raise ValueError("slippage budget cannot be negative")

@dataclass(frozen=True)
class GateDecision:
    gate: str
    status: Status
    reason: str
    evidence: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.reason:
            raise ValueError("gate decisions require reasons")
        if self.status is Status.PASS and not self.evidence:
            raise ValueError("PASS requires evidence")
