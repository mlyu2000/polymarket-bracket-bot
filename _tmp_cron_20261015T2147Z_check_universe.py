"""Resolve whether the FK Jablonec spread markets left the active universe
entirely or just diverged in question text. Substring-search all active markets."""
import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

SUBS = ["Jablonec", "Thun", "benhavn", "Kobenhavn", "Ipswich"]


async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    print(f"active markets: {len(markets)}")
    for s in SUBS:
        hits = [m for m in markets if s.lower() in m.question.lower()]
        print(f"== '{s}': {len(hits)} hit(s) ==")
        for m in hits:
            print(f"   active={m.active} closed={m.closed} liq={m.liquidity} | {m.question[:65]}")


asyncio.run(scan())
