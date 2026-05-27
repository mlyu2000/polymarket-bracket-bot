"""
Unit tests for bracket detection logic.

Formula:
  gross_edge = 1.00 - P_yes - P_no
  net_edge   = gross_edge - fee_buffer - slippage_buffer
  Valid if:   net_edge >= MIN_PROFIT_MARGIN
"""

import pytest
from unittest.mock import patch, MagicMock

from models import Market, OrderBook, BracketOpportunity
from detector import BracketDetector
from config import Config


# --- Fixtures ---

@pytest.fixture
def detector():
    return BracketDetector()


@pytest.fixture
def sample_market():
    """Active binary market with good liquidity."""
    return Market(
        id="1",
        question="Will X happen?",
        condition_id="0xabc123",
        slug="will-x-happen",
        active=True,
        closed=False,
        outcomes=["Yes", "No"],
        outcome_prices=[0.50, 0.50],
        clob_token_ids=["token_yes_1", "token_no_1"],
        volume=100000,
        liquidity=50000,
        end_date="2025-12-31",
        category="politics",
    )


@pytest.fixture
def sample_yes_book():
    """Order book with asks."""
    return OrderBook(
        market="0xabc123",
        asset_id="token_yes_1",
        bids=[{"price": "0.44", "size": "500"}],
        asks=[{"price": "0.45", "size": "200"}],
        min_order_size="5",
        tick_size="0.01",
        last_trade_price="0.44",
    )


@pytest.fixture
def sample_no_book():
    """Order book with asks."""
    return OrderBook(
        market="0xabc123",
        asset_id="token_no_1",
        bids=[{"price": "0.46", "size": "400"}],
        asks=[{"price": "0.48", "size": "300"}],
        min_order_size="5",
        tick_size="0.01",
        last_trade_price="0.47",
    )


# --- Tests ---

class TestBracketDetection:
    """Test bracket opportunity detection with safety buffers."""

    def test_basic_bracket_detected(
        self, detector, sample_market, sample_yes_book, sample_no_book
    ):
        """
        Yes=0.45, No=0.48 → gross_edge=0.07
        fee_buf=0.005, slip_buf=0.005 → net_edge=0.06 >= 0.01 ✓
        """
        with patch.object(Config, "MAX_CAPITAL_PER_TRADE", 10000):
            opp = detector.detect(sample_market, sample_yes_book, sample_no_book)

        assert opp is not None
        assert opp.yes_price == 0.45
        assert opp.no_price == 0.48
        assert opp.total_cost == 0.93
        assert opp.gross_edge == 0.07
        assert opp.net_edge == 0.06  # 0.07 - 0.005 - 0.005
        assert opp.max_shares == 200

    def test_no_bracket_when_over_dollar(
        self, detector, sample_market, sample_yes_book, sample_no_book
    ):
        """Yes + No >= 1.00 → no opportunity."""
        sample_no_book.asks[0]["price"] = "0.56"  # 0.45 + 0.56 = 1.01

        opp = detector.detect(sample_market, sample_yes_book, sample_no_book)
        assert opp is None

    def test_edge_erased_by_buffers(
        self, detector, sample_market, sample_yes_book, sample_no_book
    ):
        """
        Yes=0.495, No=0.500 → gross_edge=0.005
        fee_buf=0.005, slip_buf=0.005 → net_edge=-0.005 → filtered
        Even though raw sum (0.995) < 1.00
        """
        sample_yes_book.asks[0]["price"] = "0.495"
        sample_no_book.asks[0]["price"] = "0.500"

        opp = detector.detect(sample_market, sample_yes_book, sample_no_book)
        assert opp is None

    def test_margin_filter(
        self, detector, sample_market, sample_yes_book, sample_no_book
    ):
        """Net edge below MIN_PROFIT_MARGIN → filtered out."""
        # Yes=0.49, No=0.49 → gross=0.02, net=0.01 >= 0.01 ✓
        sample_yes_book.asks[0]["price"] = "0.49"
        sample_no_book.asks[0]["price"] = "0.49"

        opp = detector.detect(sample_market, sample_yes_book, sample_no_book)
        assert opp is not None
        assert opp.gross_edge == 0.02
        assert opp.net_edge == 0.01  # 0.02 - 0.005 - 0.005

    def test_volume_overlap(
        self, detector, sample_market, sample_yes_book, sample_no_book
    ):
        """Max shares = min(Yes volume, No volume)."""
        sample_yes_book.asks[0]["size"] = "100"
        sample_no_book.asks[0]["size"] = "300"
        sample_no_book.asks[0]["price"] = "0.48"

        with patch.object(Config, "MAX_CAPITAL_PER_TRADE", 10000):
            opp = detector.detect(sample_market, sample_yes_book, sample_no_book)
        assert opp is not None
        assert opp.max_shares == 100  # min(100, 300)

    def test_max_capital_constraint(
        self, detector, sample_market, sample_yes_book, sample_no_book
    ):
        """Shares reduced when total cost exceeds MAX_CAPITAL_PER_TRADE."""
        with patch.object(Config, "MAX_CAPITAL_PER_TRADE", 50):
            opp = detector.detect(sample_market, sample_yes_book, sample_no_book)
            assert opp is not None
            # 50 / 0.93 = 53.76 → 53 shares
            assert opp.max_shares == 53
            assert opp.max_usdc <= 50

    def test_zero_volume_no_opportunity(
        self, detector, sample_market, sample_yes_book, sample_no_book
    ):
        """No asks → no opportunity."""
        sample_yes_book.asks = []

        opp = detector.detect(sample_market, sample_yes_book, sample_no_book)
        assert opp is None

    def test_closed_market_no_opportunity(
        self, detector, sample_market, sample_yes_book, sample_no_book
    ):
        """Closed market → no opportunity."""
        sample_market.closed = True

        opp = detector.detect(sample_market, sample_yes_book, sample_no_book)
        assert opp is None

    def test_inactive_market_no_opportunity(
        self, detector, sample_market, sample_yes_book, sample_no_book
    ):
        """Inactive market → no opportunity."""
        sample_market.active = False

        opp = detector.detect(sample_market, sample_yes_book, sample_no_book)
        assert opp is None

    def test_missing_order_book(
        self, detector, sample_market, sample_yes_book
    ):
        """Missing order book → no opportunity."""
        opp = detector.detect(sample_market, sample_yes_book, None)
        assert opp is None

        opp = detector.detect(sample_market, None, sample_no_book)
        assert opp is None


class TestOpportunityCalculation:
    """Test BracketOpportunity calculations."""

    def test_potential_profit(self):
        """Profit = shares * net_edge."""
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

        assert opp.potential_profit == 6.0  # 100 * 0.06

    def test_potential_profit_zero(self):
        """Zero shares → zero profit."""
        opp = BracketOpportunity(
            market=MagicMock(question="Test", slug="test"),
            yes_price=0.45,
            no_price=0.48,
            total_cost=0.93,
            gross_edge=0.07,
            fee_buffer=0.005,
            slippage_buffer=0.005,
            net_edge=0.06,
            max_shares=0,
            max_usdc=0,
            yes_book=MagicMock(),
            no_book=MagicMock(),
        )

        assert opp.potential_profit == 0


class TestFormatOpportunity:
    """Test opportunity formatting."""

    def test_format_contains_key_info(
        self, detector, sample_market, sample_yes_book, sample_no_book
    ):
        """Formatted output contains prices, edges, shares, and profit."""
        with patch.object(Config, "MAX_CAPITAL_PER_TRADE", 10000):
            opp = detector.detect(sample_market, sample_yes_book, sample_no_book)
        assert opp is not None

        formatted = detector.format_opportunity(opp)

        assert "0.45" in formatted
        assert "0.48" in formatted
        assert "Will X happen?" in formatted
        assert "200" in formatted  # shares
        assert "BRACKET OPPORTUNITY" in formatted

    def test_format_is_readable(
        self, detector, sample_market, sample_yes_book, sample_no_book
    ):
        """Formatted output is multi-line and human-readable."""
        with patch.object(Config, "MAX_CAPITAL_PER_TRADE", 10000):
            opp = detector.detect(sample_market, sample_yes_book, sample_no_book)
        assert opp is not None

        formatted = detector.format_opportunity(opp)
        lines = formatted.split("\n")

        assert len(lines) > 10  # Multiple lines


class TestLowLiquidityFilter:
    """Test liquidity filtering."""

    def test_low_liquidity_filtered(
        self, detector, sample_market, sample_yes_book, sample_no_book
    ):
        """Market with liquidity below threshold → filtered."""
        sample_market.liquidity = 100  # Below MIN_LIQUIDITY_USDC=1000

        opp = detector.detect(sample_market, sample_yes_book, sample_no_book)
        assert opp is None

    def test_high_liquidity_allowed(
        self, detector, sample_market, sample_yes_book, sample_no_book
    ):
        """Market with sufficient liquidity → allowed."""
        sample_market.liquidity = 10000

        opp = detector.detect(sample_market, sample_yes_book, sample_no_book)
        assert opp is not None
