"""
Main loop for Polymarket Bracket Arbitrage Bot.

Polls markets → fetches order books → detects opportunities → executes/logs.
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime

from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from executor import Executor

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class Bot:
    """Main bot loop."""

    def __init__(self):
        self.api = PolymarketAPI()
        self.detector = BracketDetector()
        self.executor = Executor()
        self.running = False
        self.stats = {
            "scans": 0,
            "opportunities": 0,
            "total_profit": 0.0,
            "start_time": None,
        }

    async def scan_cycle(self) -> None:
        """One full scan cycle: fetch markets → check order books → detect."""
        self.stats["scans"] += 1

        # Fetch active markets (top by volume)
        markets = await self.api.fetch_active_markets()
        logger.debug(f"Fetched {len(markets)} active markets")

        # Check each market for bracket opportunities
        for market in markets:
            yes_token, no_token = market.clob_token_ids[0], market.clob_token_ids[1]

            yes_book, no_book = await self.api.fetch_order_books_parallel(
                yes_token, no_token
            )

            opp = self.detector.detect(market, yes_book, no_book)

            if opp:
                self.stats["opportunities"] += 1
                self.stats["total_profit"] += opp.potential_profit

                # Log formatted opportunity
                logger.info(self.detector.format_opportunity(opp))

                # Execute (dry-run or live)
                await self.executor.execute(opp)

    async def run(self) -> None:
        """Run the bot loop."""
        Config.validate()
        self.running = True
        self.stats["start_time"] = datetime.now().isoformat()

        logger.info(
            "🚀 Bracket Bot starting — mode=%s, margin=%.2f, max_capital=$%.0f",
            Config.EXECUTION_MODE,
            Config.MIN_PROFIT_MARGIN,
            Config.MAX_CAPITAL_PER_TRADE,
        )

        # Handle graceful shutdown
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: self._shutdown())

        while self.running:
            try:
                await self.scan_cycle()
            except Exception as e:
                logger.error(f"Scan cycle error: {e}", exc_info=True)

            # Sleep until next cycle
            await asyncio.sleep(Config.POLL_INTERVAL_SECONDS)

    def _shutdown(self) -> None:
        """Handle shutdown signal."""
        logger.info("🛑 Shutting down...")
        self.running = False
        self._print_stats()

    def _print_stats(self) -> None:
        """Print session statistics."""
        logger.info(
            "📊 Session stats: scans=%d, opportunities=%d, "
            "total_potential_profit=$%.2f",
            self.stats["scans"],
            self.stats["opportunities"],
            self.stats["total_profit"],
        )


async def main() -> None:
    bot = Bot()
    await bot.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
