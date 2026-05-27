"""
Unit tests for model dataclasses.
"""

import pytest
from unittest.mock import MagicMock

from models import Market, OrderBook, BracketOpportunity


class TestMarket:
    """Test Market model."""

    def test_market_creation(self):
        """Market can be instantiated with all fields."""
        m = Market(
            id="1",
            question="Will X happen?",
            condition_id="0xabc",
            slug="will-x-happen",
            active=True,
            closed=False,
            outcomes=["Yes", "No"],
            outcome_prices=[0.50, 0.50],
            clob_token_ids=["yes_1", "no_1"],
            volume=100000,
            liquidity=50000,
        )
        assert m.active is True
        assert m.closed is False
        assert len(m.outcomes) == 2
        assert len(m.clob_token_ids) == 2

    def test_market_optional_fields(self):
        """Optional fields default to None."""
        m = Market(
            id="1",
            question="Will X happen?",
            condition_id="0xabc",
            slug="will-x-happen",
            active=True,
            closed=False,
            outcomes=["Yes", "No"],
            outcome_prices=[0.50, 0.50],
            clob_token_ids=["yes_1", "no_1"],
            volume=100000,
            liquidity=50000,
        )
        assert m.end_date is None
        assert m.category is None


class TestOrderBook:
    """Test OrderBook model."""

    def test_orderbook_creation(self):
        """OrderBook can be instantiated with all fields."""
        ob = OrderBook(
            market="0xabc",
            asset_id="yes_1",
            bids=[{"price": "0.44", "size": "500"}],
            asks=[{"price": "0.46", "size": "300"}],
            min_order_size="5",
            tick_size="0.01",
        )
        assert len(ob.bids) == 1
        assert len(ob.asks) == 1
        assert ob.last_trade_price is None

    def test_orderbook_with_last_trade_price(self):
        """OrderBook stores last_trade_price when provided."""
        ob = OrderBook(
            market="0xabc",
            asset_id="yes_1",
            bids=[],
            asks=[],
            min_order_size="5",
            tick_size="0.01",
            last_trade_price="0.45",
        )
        assert ob.last_trade_price == "0.45"


class TestBracketOpportunity:
    """Test BracketOpportunity model."""

    def test_potential_profit_calculation(self):
        """Profit = max_shares * net_edge."""
        opp = BracketOpportunity(
            market=MagicMock(question="Test", slug="test"),
            yes_price=0.47,
            no_price=0.50,
            total_cost=0.97,
            gross_edge=0.03,
            fee_buffer=0.005,
            slippage_buffer=0.005,
            net_edge=0.02,
            max_shares=100,
            max_usdc=97.0,
            yes_book=MagicMock(),
            no_book=MagicMock(),
        )
        assert opp.potential_profit == 2.0  # 100 * 0.02

    def test_potential_profit_rounding(self):
        """Profit is rounded to 2 decimal places."""
        opp = BracketOpportunity(
            market=MagicMock(question="Test", slug="test"),
            yes_price=0.45,
            no_price=0.48,
            total_cost=0.93,
            gross_edge=0.07,
            fee_buffer=0.005,
            slippage_buffer=0.005,
            net_edge=0.06,
            max_shares=33,
            max_usdc=30.69,
            yes_book=MagicMock(),
            no_book=MagicMock(),
        )
        # 33 * 0.06 = 1.98 (no rounding needed)
        assert opp.potential_profit == 1.98

    def test_edge_components_consistency(self):
        """Net edge = gross_edge - fee_buffer - slippage_buffer."""
        opp = BracketOpportunity(
            market=MagicMock(question="Test", slug="test"),
            yes_price=0.45,
            no_price=0.48,
            total_cost=0.93,
            gross_edge=0.07,
            fee_buffer=0.005,
            slippage_buffer=0.005,
            net_edge=0.06,
            max_shares=100,
            max_usdc=93.0,
            yes_book=MagicMock(),
            no_book=MagicMock(),
        )
        assert opp.net_edge == pytest.approx(
            opp.gross_edge - opp.fee_buffer - opp.slippage_buffer
        )

    def test_gross_edge_from_prices(self):
        """Gross edge = 1.00 - yes_price - no_price."""
        opp = BracketOpportunity(
            market=MagicMock(question="Test", slug="test"),
            yes_price=0.45,
            no_price=0.48,
            total_cost=0.93,
            gross_edge=0.07,
            fee_buffer=0.005,
            slippage_buffer=0.005,
            net_edge=0.06,
            max_shares=100,
            max_usdc=93.0,
            yes_book=MagicMock(),
            no_book=MagicMock(),
        )
        assert opp.gross_edge == pytest.approx(1.00 - opp.yes_price - opp.no_price)
