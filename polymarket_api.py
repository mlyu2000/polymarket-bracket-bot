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
        """Fetch active binary markets, sorted by SCAN_SORT_BY. Paginates if limit > 100."""
        lim = limit or Config.MAX_MARKETS_PER_SCAN
        page_size = 100  # Gamma API hard cap per request
        markets = []
        offset = 0

        # Build sort params
        sort_field = Config.SCAN_SORT_BY
        ascending = "false" if sort_field != "liquidity" else "true"
        # For liquidity: ascending=true → lowest liquidity first (most likely to have brackets)
        # For volume/created_at: ascending=false → highest/latest first

        while offset < lim:
            batch_size = min(page_size, lim - offset)
            url = (
                f"{self.gamma_base}/markets"
                f"?limit={batch_size}&offset={offset}&active=true&closed=false"
                f"&order={sort_field}&ascending={ascending}"
            )
            raw = await self._request(url)

            if not raw:
                break  # No more pages

            for m in raw:
                # Filter: binary only (exactly 2 outcomes)
                outcomes = m.get("outcomes", [])
                if isinstance(outcomes, str):
                    outcomes = json.loads(outcomes)
                if len(outcomes) != 2:
                    continue

                outcome_prices = m.get("outcomePrices", [])
                if isinstance(outcome_prices, str):
                    outcome_prices = json.loads(outcome_prices)

                clob_token_ids = m.get("clobTokenIds", [])
                if isinstance(clob_token_ids, str):
                    clob_token_ids = json.loads(clob_token_ids)

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

            offset += len(raw)
            # Small delay between pages to avoid rate limiting
            if offset < lim:
                await asyncio.sleep(0.2)

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

    async def fetch_order_books_batch(
        self, token_pairs: list[tuple[str, str]], batch_size: int = 20
    ) -> list[tuple[Optional[OrderBook], Optional[OrderBook]]]:
        """Fetch order books for multiple markets in batches."""
        results = []
        for i in range(0, len(token_pairs), batch_size):
            batch = token_pairs[i:i + batch_size]
            tasks = [
                asyncio.gather(
                    self.fetch_order_book(yes_id),
                    self.fetch_order_book(no_id),
                )
                for yes_id, no_id in batch
            ]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
            if i + batch_size < len(token_pairs):
                await asyncio.sleep(0.1)  # Small delay between batches
        return results
