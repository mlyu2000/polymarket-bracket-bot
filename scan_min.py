import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=100)
    results = []
    for m in markets:
        if m.liquidity < 100:
            continue
        yes_book = await api.fetch_order_book(m.clob_token_ids[0])
        no_book = await api.fetch_order_book(m.clob_token_ids[1])
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yes_best = min(float(a['price']) for a in yes_book.asks)
        no_best = min(float(a['price']) for a in no_book.asks)
        total = yes_best + no_best
        if total < 1.01:
            results.append((total, m.question[:80], yes_best, no_best, m.liquidity))
    results.sort(key=lambda x: x[0])
    for r in results[:20]:
        print(r)

asyncio.run(scan())
