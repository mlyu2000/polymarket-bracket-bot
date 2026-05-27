"""
Detection engine for bracket arbitrage opportunities.

Core math:
  gross_edge = 1.00 - P_yes - P_no
  net_edge   = gross_edge - fee_buffer - slippage_buffer
  Opportunity valid if net_edge >= MIN_PROFIT_MARGIN
"""

from typing import Optional

from config import Config
from models import Market, OrderBook, BracketOpportunity


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

        # Guard: invalid prices (zero or >= 1.0)
        if yes_price <= 0 or no_price <= 0:
            return None
        if yes_price >= 1.0 or no_price >= 1.0:
            return None

        # Available volume at best ask
        yes_volume = int(yes_ask["size"])
        no_volume = int(no_ask["size"])

        # Overlap: min of both sides
        max_shares = min(yes_volume, no_volume)

        if max_shares <= 0:
            return None

        total_cost = yes_price + no_price

        # Edge calculation with safety buffers
        gross_edge = 1.00 - total_cost
        fee_buffer = Config.FEE_BUFFER
        slippage_buffer = Config.SLIPPAGE_BUFFER
        net_edge = gross_edge - fee_buffer - slippage_buffer

        # Check margin threshold (net edge must be sufficient)
        if net_edge < Config.MIN_PROFIT_MARGIN:
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
            gross_edge=round(gross_edge, 4),
            fee_buffer=fee_buffer,
            slippage_buffer=slippage_buffer,
            net_edge=round(net_edge, 4),
            max_shares=max_shares,
            max_usdc=round(max_usdc, 2),
            yes_book=yes_book,
            no_book=no_book,
        )

    def format_opportunity(self, opp: BracketOpportunity) -> str:
        """Format opportunity for console logging."""
        lines = [
            "═" * 60,
            "📊 BRACKET OPPORTUNITY DETECTED",
            "═" * 60,
            f"Market: {opp.market.question}",
            f"Slug:   {opp.market.slug}",
            f"Volume: ${opp.market.volume:,.0f}",
            "",
            f"Yes Ask: ${opp.yes_price:.3f}",
            f"No  Ask: ${opp.no_price:.3f}",
            f"Gross cost: ${opp.total_cost:.3f}",
            f"Gross edge: ${opp.gross_edge:.3f}",
            f"Fee buffer:  -${opp.fee_buffer:.3f}",
            f"Slippage:    -${opp.slippage_buffer:.3f}",
            f"Net edge/pair: ${opp.net_edge:.3f}",
            "",
            f"Max shares: {opp.max_shares}",
            f"Max USDC:   ${opp.max_usdc:,.2f}",
            f"Potential profit: ${opp.potential_profit:,.2f}",
            f"ROI: {(opp.potential_profit / opp.max_usdc * 100):.1f}%",
            "═" * 60,
        ]
        return "\n".join(lines)
