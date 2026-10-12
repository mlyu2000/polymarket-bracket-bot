import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def check():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    print("Total markets", len(markets))
    count = 0
    for m in markets:
        if m.liquidity < 100:
            continue
        yes_book = await api.fetch_order_book(m.clob_token_ids[0])
        no_book = await api.fetch_order_book(m.clob_token_ids[1])
        if not yes_book or not no_book:
            continue
        try:
            yes_best = min(float(a['price']) for a in yes_book.asks)
            no_best = min(float(a['price']) for a in no_book.asks)
        except:
            continue
        total = yes_best + no_best
        if total < 1.0:
            count += 1
            print("BRACKET FOUND:", m.question[:80], total, yes_best, no_best, m.liquidity)
        if count >= 10:
            break
    print("Found", count)

asyncio.run(check())
