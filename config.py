"""
Configuration for Polymarket Bracket Arbitrage Bot.

Safety defaults — do not change without understanding the risks.
"""

from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")
import os


class Config:
    """Bot configuration with safety defaults."""

    # --- Execution Mode ---
    EXECUTION_MODE: str = os.getenv("EXECUTION_MODE", "dry_run")  # dry_run | live

    # --- Profit Thresholds ---
    MIN_PROFIT_MARGIN: float = float(
        os.getenv("MIN_PROFIT_MARGIN", "0.01")
    )  # $0.01 per pair minimum (net edge after buffers)
    MAX_CAPITAL_PER_TRADE: float = float(
        os.getenv("MAX_CAPITAL_PER_TRADE", "50")
    )  # $50 USDC max per trade

    # --- Safety Buffers ---
    FEE_BUFFER: float = float(
        os.getenv("FEE_BUFFER", "0.005")
    )  # 0.5¢ buffer for Polymarket taker fees
    SLIPPAGE_BUFFER: float = float(
        os.getenv("SLIPPAGE_BUFFER", "0.005")
    )  # 0.5¢ buffer for stale data / slippage

    # --- Scan Settings ---
    POLL_INTERVAL_SECONDS: float = float(
        os.getenv("POLL_INTERVAL_SECONDS", "5")
    )  # 5s polling
    MAX_MARKETS_PER_SCAN: int = int(
        os.getenv("MAX_MARKETS_PER_SCAN", "100")
    )  # Top N by volume
    MIN_LIQUIDITY_USDC: float = float(
        os.getenv("MIN_LIQUIDITY_USDC", "1000")
    )  # Skip markets with < $1000 liquidity

    # --- API Settings ---
    GAMMA_API_BASE: str = "https://gamma-api.polymarket.com"
    CLOB_API_BASE: str = "https://clob.polymarket.com"
    DATA_API_BASE: str = "https://data-api.polymarket.com"
    REQUEST_TIMEOUT: float = float(os.getenv("REQUEST_TIMEOUT", "10"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RATE_LIMIT_BACKOFF_BASE: float = float(
        os.getenv("RATE_LIMIT_BACKOFF_BASE", "2")
    )  # Exponential backoff base

    # --- Logging ---
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_OPPORTUNITIES_FILE: str = os.getenv(
        "LOG_OPPORTUNITIES_FILE", "opportunities.log"
    )

    @classmethod
    def validate(cls) -> None:
        """Validate configuration at startup."""
        if cls.EXECUTION_MODE not in ("dry_run", "live"):
            raise ValueError(f"Invalid EXECUTION_MODE: {cls.EXECUTION_MODE}")
        if cls.MIN_PROFIT_MARGIN <= 0:
            raise ValueError("MIN_PROFIT_MARGIN must be > 0")
        if cls.MAX_CAPITAL_PER_TRADE <= 0:
            raise ValueError("MAX_CAPITAL_PER_TRADE must be > 0")
        if cls.POLL_INTERVAL_SECONDS < 1:
            raise ValueError("POLL_INTERVAL_SECONDS must be >= 1")
        if cls.FEE_BUFFER < 0:
            raise ValueError("FEE_BUFFER must be >= 0")
        if cls.SLIPPAGE_BUFFER < 0:
            raise ValueError("SLIPPAGE_BUFFER must be >= 0")
        if cls.MAX_MARKETS_PER_SCAN < 1:
            raise ValueError("MAX_MARKETS_PER_SCAN must be >= 1")


if __name__ == "__main__":
    Config.validate()
    print(f"✓ Config validated: mode={Config.EXECUTION_MODE}, "
          f"margin={Config.MIN_PROFIT_MARGIN}, max_capital={Config.MAX_CAPITAL_PER_TRADE}")
