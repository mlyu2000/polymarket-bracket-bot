"""
Paper execution engine for Polymarket Bracket Bot.

Simulates realistic fill scenarios for testing the execution logic
before going live. Supports:
- Both legs filled
- One leg filled (leg-in risk)
- Neither leg filled
- Price moved before execution
- Partial fills
"""

import logging
import random
from dataclasses import dataclass, field
from typing import Literal

from config import Config
from models import BracketOpportunity, Market, OrderBook

logger = logging.getLogger(__name__)

FillOutcome = Literal["filled", "partial", "rejected", "price_moved"]


@dataclass
class PaperFill:
    """Result of a simulated order fill."""
    side: str  # "YES" or "NO"
    outcome: FillOutcome
    price: float
    size: int
    message: str


@dataclass
class PaperExecutionResult:
    """Result of a simulated bracket execution."""
    opportunity: BracketOpportunity
    yes_fill: PaperFill
    no_fill: PaperFill
    unhedged: bool
    unwind_triggered: bool
    final_pnl: float
    log_lines: list[str] = field(default_factory=list)


class PaperExecutor:
    """Simulates bracket execution with realistic fill scenarios."""

    def __init__(
        self,
        fill_rate: float = 0.8,
        partial_fill_rate: float = 0.1,
        price_move_rate: float = 0.05,
        slippage_pct: float = 0.01,
        seed: int | None = None,
    ):
        self.fill_rate = fill_rate
        self.partial_fill_rate = partial_fill_rate
        self.price_move_rate = price_move_rate
        self.slippage_pct = slippage_pct
        self.rng = random.Random(seed)
        self.stats = {
            "attempts": 0,
            "both_filled": 0,
            "one_leg": 0,
            "neither": 0,
            "unwind": 0,
            "total_pnl": 0.0,
        }

    def execute(self, opp: BracketOpportunity) -> PaperExecutionResult:
        """Simulate bracket execution for a given opportunity."""
        self.stats["attempts"] += 1
        log = []

        log.append(f"[PAPER] Attempting bracket:")
        log.append(f"  Market: {opp.market.question}")
        log.append(f"  YES ${opp.yes_price:.3f} x {opp.max_shares}")
        log.append(f"  NO  ${opp.no_price:.3f} x {opp.max_shares}")

        # Simulate YES fill
        yes_fill = self._simulate_fill("YES", opp.yes_price, opp.max_shares)
        log.append(f"[PAPER] YES: {yes_fill.message}")

        # Simulate NO fill
        no_fill = self._simulate_fill("NO", opp.no_price, opp.max_shares)
        log.append(f"[PAPER] NO:  {no_fill.message}")

        # Check for unhedged position (leg-in risk)
        unhedged = (
            (yes_fill.outcome in ("filled", "partial") and no_fill.outcome in ("rejected", "price_moved"))
            or (no_fill.outcome in ("filled", "partial") and yes_fill.outcome in ("rejected", "price_moved"))
        )

        unwind_triggered = False
        final_pnl = 0.0

        if unhedged:
            self.stats["one_leg"] += 1
            log.append("[PAPER] ⚠️  Unhedged position detected.")
            log.append("[PAPER] 🚨 Emergency unwind simulated.")
            unwind_triggered = True
            self.stats["unwind"] += 1

            # Calculate PnL for unhedged scenario
            if yes_fill.outcome in ("filled", "partial") and no_fill.outcome in ("rejected", "price_moved"):
                # Long YES, unwind at bid (simulate 2% slippage)
                unwind_price = yes_fill.price * (1 - 0.02)
                loss = (unwind_price - yes_fill.price) * yes_fill.size
                final_pnl = round(loss, 2)
                log.append(f"[PAPER] Sold YES at ${unwind_price:.3f} (was ${yes_fill.price:.3f})")
                log.append(f"[PAPER] Unwind loss: ${abs(final_pnl):.2f}")
            else:
                # Long NO, unwind at bid
                unwind_price = no_fill.price * (1 - 0.02)
                loss = (unwind_price - no_fill.price) * no_fill.size
                final_pnl = round(loss, 2)
                log.append(f"[PAPER] Sold NO at ${unwind_price:.3f} (was ${no_fill.price:.3f})")
                log.append(f"[PAPER] Unwind loss: ${abs(final_pnl):.2f}")

        elif yes_fill.outcome in ("filled", "partial") and no_fill.outcome in ("filled", "partial"):
            # Both legs filled (or partial)
            filled_size = min(yes_fill.size, no_fill.size)
            net_edge = opp.net_edge
            profit = round(filled_size * net_edge, 2)
            final_pnl = profit

            if filled_size == opp.max_shares:
                self.stats["both_filled"] += 1
            else:
                self.stats["one_leg"] += 1  # Partial counts as one_leg for stats

            log.append(f"[PAPER] ✅ Bracket locked. Size: {filled_size}")
            log.append(f"[PAPER] Profit: ${profit:.2f} ({net_edge * 100:.1f}% per pair)")
        else:
            # Neither filled
            self.stats["neither"] += 1
            log.append("[PAPER] ❌ Both legs failed. No position.")

        self.stats["total_pnl"] += final_pnl

        return PaperExecutionResult(
            opportunity=opp,
            yes_fill=yes_fill,
            no_fill=no_fill,
            unhedged=unhedged,
            unwind_triggered=unwind_triggered,
            final_pnl=final_pnl,
            log_lines=log,
        )

    def _simulate_fill(self, side: str, price: float, size: int) -> PaperFill:
        """Simulate a single leg fill."""
        roll = self.rng.random()

        if roll < self.price_move_rate:
            # Price moved away
            new_price = price * (1 + self.rng.uniform(0.005, 0.03))
            return PaperFill(
                side=side,
                outcome="price_moved",
                price=new_price,
                size=0,
                message=f"Price moved to ${new_price:.3f} (was ${price:.3f})",
            )

        if roll < self.price_move_rate + (1 - self.fill_rate - self.partial_fill_rate):
            # Rejected
            return PaperFill(
                side=side,
                outcome="rejected",
                price=price,
                size=0,
                message=f"Order rejected (simulated latency)",
            )

        if roll < self.price_move_rate + (1 - self.fill_rate):
            # Partial fill
            fill_size = max(1, int(size * self.rng.uniform(0.2, 0.8)))
            slippage = price * (1 + self.rng.uniform(0, self.slippage_pct))
            return PaperFill(
                side=side,
                outcome="partial",
                price=round(slippage, 3),
                size=fill_size,
                message=f"Partial fill: {fill_size}/{size} @ ${slippage:.3f}",
            )

        # Full fill
        slippage = price * (1 + self.rng.uniform(0, self.slippage_pct))
        return PaperFill(
            side=side,
            outcome="filled",
            price=round(slippage, 3),
            size=size,
            message=f"Filled {size} @ ${slippage:.3f}",
        )

    def print_stats(self) -> None:
        """Print paper trading statistics."""
        total = self.stats["attempts"]
        if total == 0:
            logger.info("No paper executions yet.")
            return

        logger.info(
            "📊 Paper Stats: attempts=%d, both=%d, one_leg=%d, neither=%d, "
            "unwind=%d, total_pnl=$%.2f",
            total,
            self.stats["both_filled"],
            self.stats["one_leg"],
            self.stats["neither"],
            self.stats["unwind"],
            self.stats["total_pnl"],
        )
