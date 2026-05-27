"""
Polymarket API client.

Public, read-only endpoints — no authentication required.
"""

import asyncio
import json
from typing import Optional

import httpx

from config import Config
from models import Market, OrderBook


class PolymarketAPI:
    """Async client for Polymarket Gamma + CLOB APIs."""

    def __init__(self):
        self.gamma_base = Config.GAMMA_API_BASE
        self.clob_base = Config.CLOB_API_BASE
        self.timeout = Config.REQUEST_TIMEOUT
        self.max_retries = Config.MAX_RETRIES
        self.backoff_base = Config.RATE_LIMIT_BACKOFF_BASE

    async def _request(self, url: str, retries: int = 0) -> dict:
        """Make a GET request with exponential backoff on 429."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(url)
                if resp.status_code == 429:
                    if retries < self.max_retries:
                        wait = self.backoff_base ** retries
                        await asyncio.sleep(wait)
                        return await self._request(url, retries + 1)
                    raise RuntimeError(f"Rate limited after {retries} retries: {url}")
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as e:
                if retries < self.max_retries:
                    wait = self.backoff_base ** retries
                    await asyncio.sleep(wait)
                    return await self._request(url, retries + 1)
                raise e

    async def fetch_active_markets(
        self, limit: int | None = None
    ) -> list[Market]:
        """Fetch active binary markets, sorted by volume."""
        lim = limit or Config.MAX_MARKETS_PER_SCAN
        url = (
            f"{self.gamma_base}/markets"
            f"?limit={lim}&active=true&closed=false"
            f"&order=volume&ascending=false"
        )
        raw = await self._request(url)

        markets = []
        for m in raw:
            # Filter: binary only (exactly 2 outcomes)
            outcomes = json.loads(m.get("outcomes", "[]"))
            if len(outcomes) != 2:
                continue

            outcome_prices = json.loads(m.get("outcomePrices", "[]"))
            clob_token_ids = json.loads(m.get("clobTokenIds", "[]"))

            if len(clob_token_ids) != 2:
                continue

            markets.append(Market(
                id=m.get("id", ""),
                question=m.get("question", ""),
                condition_id=m.get("conditionId", ""),
                slug=m.get("slug", ""),
                active=m.get("active", False),
                closed=m.get("closed", True),
                outcomes=outcomes,
                outcome_prices=[float(p) for p in outcome_prices],
                clob_token_ids=clob_token_ids,
                volume=float(m.get("volume", 0)),
                liquidity=float(m.get("liquidity", 0)),
                end_date=m.get("endDate"),
                category=m.get("category"),
            ))

        return markets

    async def fetch_order_book(self, token_id: str) -> Optional[OrderBook]:
        """Fetch L2 order book for a single token."""
        url = f"{self.clob_base}/book?token_id={token_id}"
        try:
            data = await self._request(url)
            return OrderBook(
                market=data.get("market", ""),
                asset_id=data.get("asset_id", ""),
                bids=data.get("bids", []),
                asks=data.get("asks", []),
                min_order_size=data.get("min_order_size", "5"),
                tick_size=data.get("tick_size", "0.01"),
                last_trade_price=data.get("last_trade_price"),
            )
        except Exception:
            return None

    async def fetch_order_books_parallel(
        self, yes_token_id: str, no_token_id: str
    ) -> tuple[Optional[OrderBook], Optional[OrderBook]]:
        """Fetch Yes and No order books concurrently."""
        yes_book, no_book = await asyncio.gather(
            self.fetch_order_book(yes_token_id),
            self.fetch_order_book(no_token_id),
        )
        return yes_book, no_book
