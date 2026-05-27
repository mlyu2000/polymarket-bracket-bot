"""
Unit tests for bracket detection logic.
"""

import pytest
from unittest.mock import patch, MagicMock

from polymarket_api import Market, OrderBook
from detector import BracketDetector, BracketOpportunity
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
    """Test bracket opportunity detection."""

    def test_basic_bracket_detected(
        self, detector, sample_market, sample_yes_book, sample_no_book
    ):
        """Ask(Yes)=0.45 + Ask(No)=0.48 = 0.93 < 1.00 - 0.02 → detected."""
        with patch.object(Config, "MAX_CAPITAL_PER_TRADE", 10000):
            opp = detector.detect(sample_market, sample_yes_book, sample_no_book)

        assert opp is not None
        assert opp.yes_price == 0.45
        assert opp.no_price == 0.48
        assert opp.total_cost == 0.93
        assert opp.profit_per_pair == 0.07
        # min(200, 300) = 200 shares
        assert opp.max_shares == 200

    def test_no_bracket_when_over_dollar(
        self, detector, sample_market, sample_yes_book, sample_no_book
    ):
        """Ask(Yes) + Ask(No) >= 1.00 → no opportunity."""
        sample_no_book.asks[0]["price"] = "0.56"  # 0.45 + 0.56 = 1.01

        opp = detector.detect(sample_market, sample_yes_book, sample_no_book)
        assert opp is None

    def test_margin_filter(
        self, detector, sample_market, sample_yes_book, sample_no_book
    ):
        """Profit margin below MIN_PROFIT_MARGIN → filtered out."""
        # 0.45 + 0.52 = 0.97, profit = 0.03 > 0.02 ✓
        sample_no_book.asks[0]["price"] = "0.52"
        opp = detector.detect(sample_market, sample_yes_book, sample_no_book)
        assert opp is not None
        assert opp.profit_per_pair == 0.03

        # 0.45 + 0.53 = 0.98, profit = 0.02 == 0.02 ✓ (equal is OK)
        sample_no_book.asks[0]["price"] = "0.53"
        opp = detector.detect(sample_market, sample_yes_book, sample_no_book)
        assert opp is not None

        # 0.45 + 0.54 = 0.99, profit = 0.01 < 0.02 → filtered
        sample_no_book.asks[0]["price"] = "0.54"
        opp = detector.detect(sample_market, sample_yes_book, sample_no_book)
        assert opp is None

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
        # 200 shares * $0.93 = $186 > $50 max → reduce
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
        """Profit = shares * profit_per_pair."""
        opp = BracketOpportunity(
            market=MagicMock(question="Test", slug="test"),
            yes_price=0.45,
            no_price=0.48,
            total_cost=0.93,
            profit_per_pair=0.07,
            max_shares=100,
            max_usdc=93.0,
            yes_book=MagicMock(),
            no_book=MagicMock(),
        )

        assert opp.potential_profit == 7.0  # 100 * 0.07

    def test_potential_profit_zero(self):
        """Zero shares → zero profit."""
        opp = BracketOpportunity(
            market=MagicMock(question="Test", slug="test"),
            yes_price=0.45,
            no_price=0.48,
            total_cost=0.93,
            profit_per_pair=0.07,
            max_shares=0,
            max_usdc=0,
            yes_book=MagicMock(),
            no_book=MagicMock(),
        )

        assert opp.potential_profit == 0


class TestFormatOpportunity:
    """Test opportunity formatting."""

    def test_format_contains_key_info(self, detector, sample_market, sample_yes_book, sample_no_book):
        """Formatted output contains prices, shares, and profit."""
        with patch.object(Config, "MAX_CAPITAL_PER_TRADE", 10000):
            opp = detector.detect(sample_market, sample_yes_book, sample_no_book)
        assert opp is not None

        formatted = detector.format_opportunity(opp)

        assert "0.45" in formatted
        assert "0.48" in formatted
        assert "0.93" in formatted
        assert "Will X happen?" in formatted
        assert "200" in formatted  # shares

    def test_format_is_readable(self, detector, sample_market, sample_yes_book, sample_no_book):
        """Formatted output is multi-line and human-readable."""
        opp = detector.detect(sample_market, sample_yes_book, sample_no_book)
        assert opp is not None

        formatted = detector.format_opportunity(opp)
        lines = formatted.split("\n")

        assert len(lines) > 5  # Multiple lines
        assert any("BRACKET OPPORTUNITY" in line for line in lines)


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
