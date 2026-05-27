"""
Execution router.

MVP: Dry-run mode only. Logs opportunities to console and file.
Future: Live mode with wallet signatures.
"""

import logging
from pathlib import Path
from datetime import datetime

from config import Config
from detector import BracketOpportunity

logger = logging.getLogger(__name__)


class Executor:
    """Execute or log bracket opportunities."""

    def __init__(self):
        self.mode = Config.EXECUTION_MODE
        self.log_file = Path(Config.LOG_OPPORTUNITIES_FILE)

    async def execute(self, opportunity: BracketOpportunity) -> None:
        """Handle a detected opportunity based on execution mode."""
        if self.mode == "dry_run":
            await self._dry_run(opportunity)
        elif self.mode == "live":
            await self._live(opportunity)
        else:
            logger.warning(f"Unknown execution mode: {self.mode}")

    async def _dry_run(self, opp: BracketOpportunity) -> None:
        """Log opportunity without executing trades."""
        timestamp = datetime.now().isoformat()
        log_entry = (
            f"{timestamp} | DRY_RUN | "
            f"{opp.market.question} | "
            f"Yes@{opp.yes_price:.3f} No@{opp.no_price:.3f} | "
            f"Total={opp.total_cost:.3f} | "
            f"Shares={opp.max_shares} | "
            f"USDC=${opp.max_usdc:,.2f} | "
            f"Profit=${opp.potential_profit:,.2f}"
        )

        # Console output
        logger.info(
            "DRY_RUN: Yes@%.3f No@%.3f Total=%.3f "
            "Shares=%d USDC=$%.2f Profit=$%.2f | %s",
            opp.yes_price,
            opp.no_price,
            opp.total_cost,
            opp.max_shares,
            opp.max_usdc,
            opp.potential_profit,
            opp.market.question[:50],
        )

        # Append to log file
        self.log_file.write_text(
            self.log_file.read_text(errors="ignore") + log_entry + "\n"
        )

    async def _live(self, opp: BracketOpportunity) -> None:
        """TODO: Implement live execution with wallet signatures."""
        raise NotImplementedError("Live execution not yet implemented")
