"""
Models for Polymarket Bracket Arbitrage Bot.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Market:
    """A binary market from Gamma API."""
    id: str
    question: str
    condition_id: str
    slug: str
    active: bool
    closed: bool
    outcomes: list[str]
    outcome_prices: list[float]
    clob_token_ids: list[str]
    volume: float
    liquidity: float
    end_date: Optional[str] = None
    category: Optional[str] = None


@dataclass
class OrderBook:
    """L2 order book from CLOB API."""
    market: str  # condition_id
    asset_id: str  # token_id
    bids: list[dict]  # [{"price": "0.64", "size": "500"}]
    asks: list[dict]  # [{"price": "0.66", "size": "300"}]
    min_order_size: str
    tick_size: str
    last_trade_price: Optional[str] = None


@dataclass
class BracketOpportunity:
    """A detected bracket arbitrage opportunity."""
    market: Market
    yes_price: float
    no_price: float
    total_cost: float
    gross_edge: float
    fee_buffer: float
    slippage_buffer: float
    net_edge: float
    max_shares: int
    max_usdc: float
    yes_book: OrderBook
    no_book: OrderBook

    @property
    def potential_profit(self) -> float:
        """Total profit = shares * net_edge."""
        return round(self.max_shares * self.net_edge, 2)
