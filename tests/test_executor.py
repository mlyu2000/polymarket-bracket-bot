"""
Unit tests for executor (dry-run mode).
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

from models import BracketOpportunity
from executor import Executor
from config import Config


@pytest.fixture
def sample_opportunity():
    """A sample bracket opportunity for testing."""
    return BracketOpportunity(
        market=MagicMock(
            question="Will X happen?",
            slug="will-x-happen",
        ),
        yes_price=0.45,
        no_price=0.48,
        total_cost=0.93,
        gross_edge=0.07,
        fee_buffer=0.005,
        slippage_buffer=0.005,
        net_edge=0.06,
        max_shares=53,
        max_usdc=49.29,
        yes_book=MagicMock(),
        no_book=MagicMock(),
    )


class TestExecutor:
    """Test Executor dry-run mode."""

    def test_executor_init_dry_run(self):
        """Executor defaults to dry_run mode."""
        with patch.object(Config, "EXECUTION_MODE", "dry_run"):
            executor = Executor()
            assert executor.mode == "dry_run"

    def test_executor_init_live(self):
        """Executor respects live mode config."""
        with patch.object(Config, "EXECUTION_MODE", "live"):
            executor = Executor()
            assert executor.mode == "live"

    @pytest.mark.asyncio
    async def test_dry_run_no_side_effects(self, sample_opportunity):
        """Dry run should not raise errors or execute trades."""
        with patch.object(Config, "EXECUTION_MODE", "dry_run"):
            executor = Executor()
            # Should complete without raising
            await executor.execute(sample_opportunity)

    @pytest.mark.asyncio
    async def test_live_raises_not_implemented(self, sample_opportunity):
        """Live mode should raise NotImplementedError."""
        with patch.object(Config, "EXECUTION_MODE", "live"):
            executor = Executor()
            with pytest.raises(NotImplementedError):
                await executor.execute(sample_opportunity)

    @pytest.mark.asyncio
    async def test_unknown_mode_logs_warning(self, sample_opportunity, caplog):
        """Unknown mode should log a warning."""
        with patch.object(Config, "EXECUTION_MODE", "unknown"):
            executor = Executor()
            await executor.execute(sample_opportunity)
            assert "Unknown execution mode: unknown" in caplog.text
