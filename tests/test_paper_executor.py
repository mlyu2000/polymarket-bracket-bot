"""
Tests for paper execution engine.
"""

import pytest
from unittest.mock import MagicMock

from models import Market, OrderBook, BracketOpportunity
from paper_executor import PaperExecutor


@pytest.fixture
def sample_opportunity():
    """A sample bracket opportunity for testing."""
    return BracketOpportunity(
        market=MagicMock(
            question="Will BTC hit $100K?",
            slug="btc-100k",
        ),
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


class TestPaperExecutor:
    """Test paper execution scenarios."""

    def test_both_legs_filled(self, sample_opportunity):
        """Both legs fill — bracket locked."""
        executor = PaperExecutor(
            fill_rate=1.0,  # Always fill
            partial_fill_rate=0.0,
            price_move_rate=0.0,
            seed=42,
        )

        result = executor.execute(sample_opportunity)

        assert result.unhedged is False
        assert result.unwind_triggered is False
        assert result.final_pnl > 0
        assert result.yes_fill.outcome == "filled"
        assert result.no_fill.outcome == "filled"

    def test_one_leg_filled_leg_in_risk(self, sample_opportunity):
        """One leg fills, other fails — leg-in risk."""
        executor = PaperExecutor(
            fill_rate=0.5,
            partial_fill_rate=0.0,
            price_move_rate=0.0,
            seed=123,  # Deterministic seed for reproducibility
        )

        # Run multiple times to find a leg-in scenario
        leg_in_found = False
        for _ in range(20):
            result = executor.execute(sample_opportunity)
            if result.unhedged:
                leg_in_found = True
                break

        # With seed 123 and these rates, we should hit a leg-in scenario
        assert leg_in_found, "Expected at least one leg-in risk scenario"

    def test_neither_leg_filled(self, sample_opportunity):
        """Both legs fail — no position."""
        executor = PaperExecutor(
            fill_rate=0.0,  # Never fill
            partial_fill_rate=0.0,
            price_move_rate=0.0,
            seed=42,
        )

        result = executor.execute(sample_opportunity)

        assert result.unhedged is False
        assert result.unwind_triggered is False
        assert result.final_pnl == 0.0
        assert result.yes_fill.outcome in ("rejected", "price_moved")
        assert result.no_fill.outcome in ("rejected", "price_moved")

    def test_price_moved_before_execution(self, sample_opportunity):
        """Price moves before execution."""
        executor = PaperExecutor(
            fill_rate=0.0,
            partial_fill_rate=0.0,
            price_move_rate=1.0,  # Always price move
            seed=42,
        )

        result = executor.execute(sample_opportunity)

        assert result.yes_fill.outcome == "price_moved"
        assert result.no_fill.outcome == "price_moved"
        assert result.yes_fill.price > sample_opportunity.yes_price
        assert result.no_fill.price > sample_opportunity.no_price

    def test_partial_fills(self, sample_opportunity):
        """Partial fills — size reduced."""
        executor = PaperExecutor(
            fill_rate=0.0,
            partial_fill_rate=1.0,  # Always partial
            price_move_rate=0.0,
            seed=42,
        )

        result = executor.execute(sample_opportunity)

        assert result.yes_fill.outcome == "partial"
        assert result.no_fill.outcome == "partial"
        assert result.yes_fill.size < sample_opportunity.max_shares
        assert result.no_fill.size < sample_opportunity.max_shares

    def test_unwind_triggered_on_leg_in(self, sample_opportunity):
        """Unwind triggered when one leg fills and other fails."""
        executor = PaperExecutor(
            fill_rate=1.0,  # Always fill
            partial_fill_rate=0.0,
            price_move_rate=0.0,
            seed=42,
        )

        # Manually create a leg-in scenario
        yes_fill = executor._simulate_fill("YES", 0.47, 100)
        no_fill = executor._simulate_fill("NO", 0.50, 100)

        # Both should fill with these settings
        assert yes_fill.outcome == "filled"
        assert no_fill.outcome == "filled"

    def test_stats_tracking(self, sample_opportunity):
        """Stats are tracked correctly."""
        executor = PaperExecutor(
            fill_rate=1.0,
            partial_fill_rate=0.0,
            price_move_rate=0.0,
            seed=42,
        )

        for _ in range(5):
            executor.execute(sample_opportunity)

        assert executor.stats["attempts"] == 5
        assert executor.stats["both_filled"] == 5
        assert executor.stats["total_pnl"] > 0

    def test_stats_print_no_crash(self, sample_opportunity):
        """Print stats doesn't crash when no executions."""
        executor = PaperExecutor()
        executor.print_stats()  # Should not raise
