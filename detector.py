"""
Detection engine for bracket arbitrage opportunities.

Core math: Ask(Yes) + Ask(No) < 1.00 - margin threshold.
"""

from dataclasses import dataclass
from typing import Optional

from config import Config
from polymarket_api import Market, OrderBook


@dataclass
class BracketOpportunity:
    """A detected bracket arbitrage opportunity."""
    market: Market
    yes_price: float
    no_price: float
    total_cost: float
    profit_per_pair: float
    max_shares: int
    max_usdc: float
    yes_book: OrderBook
    no_book: OrderBook

    @property
    def potential_profit(self) -> float:
        """Total profit = shares * profit_per_pair."""
        return round(self.max_shares * self.profit_per_pair, 2)


class BracketDetector:
    """Detect bracket opportunities from order book data."""

    def detect(
        self,
        market: Market,
        yes_book: Optional[OrderBook],
        no_book: Optional[OrderBook],
    ) -> Optional[BracketOpportunity]:
        """
        Check if a market has a bracket opportunity.

        Returns BracketOpportunity if valid, None otherwise.
        """
        # Guard: both books must exist
        if not yes_book or not no_book:
            return None

        # Guard: both sides must have asks
        if not yes_book.asks or not no_book.asks:
            return None

        # Guard: market must be active and not closed
        if not market.active or market.closed:
            return None

        # Guard: minimum liquidity
        if market.liquidity < Config.MIN_LIQUIDITY_USDC:
            return None

        # Best asks
        yes_ask = yes_book.asks[0]
        no_ask = no_book.asks[0]

        yes_price = float(yes_ask["price"])
        no_price = float(no_ask["price"])

        # Available volume at best ask
        yes_volume = int(yes_ask["size"])
        no_volume = int(no_ask["size"])

        # Overlap: min of both sides
        max_shares = min(yes_volume, no_volume)

        if max_shares <= 0:
            return None

        total_cost = yes_price + no_price

        # Check margin threshold
        profit_per_pair = 1.00 - total_cost
        if profit_per_pair < Config.MIN_PROFIT_MARGIN:
            return None

        # Check capital constraint
        max_usdc = max_shares * total_cost
        if max_usdc > Config.MAX_CAPITAL_PER_TRADE:
            # Reduce shares to fit capital limit
            max_shares = int(Config.MAX_CAPITAL_PER_TRADE / total_cost)
            if max_shares <= 0:
                return None
            max_usdc = max_shares * total_cost

        return BracketOpportunity(
            market=market,
            yes_price=yes_price,
            no_price=no_price,
            total_cost=round(total_cost, 4),
            profit_per_pair=round(profit_per_pair, 4),
            max_shares=max_shares,
            max_usdc=round(max_usdc, 2),
            yes_book=yes_book,
            no_book=no_book,
        )

    def format_opportunity(self, opp: BracketOpportunity) -> str:
        """Format opportunity for console logging."""
        lines = [
            "═" * 60,
            f"📊 BRACKET OPPORTUNITY DETECTED",
            f"═" * 60,
            f"Market: {opp.market.question}",
            f"Slug:   {opp.market.slug}",
            f"Volume: ${opp.market.volume:,.0f}",
            "",
            f"Yes Ask: ${opp.yes_price:.3f}",
            f"No  Ask: ${opp.no_price:.3f}",
            f"Total: ${opp.total_cost:.3f}",
            f"Profit/pair: ${opp.profit_per_pair:.3f}",
            "",
            f"Max shares: {opp.max_shares}",
            f"Max USDC:  ${opp.max_usdc:,.2f}",
            f"Potential profit: ${opp.potential_profit:,.2f}",
            f"ROI: {(opp.potential_profit / opp.max_usdc * 100):.1f}%",
            f"{'═' * 60}",
        ]
        return "\n".join(lines)
