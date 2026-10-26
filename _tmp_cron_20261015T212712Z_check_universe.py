"""Resolve whether Thun/Kobenhavn/PA-House left the active universe or the
question text just diverged. Substring-search all active markets.
"""
import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

SUBS = ["Thun", "benhavn", "Kobenhavn", "Pennsylvania", "House seats"]


async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    print(f"active markets: {len(markets)}")
    for s in SUBS:
        hits = [m for m in markets if s.lower() in m.question.lower()]
        print(f"\n== '{s}': {len(hits)} hit(s) ==")
        for m in hits:
            print(f"   active={m.active} closed={m.closed} liq={m.liquidity} | {m.question[:60]}")


asyncio.run(scan())
