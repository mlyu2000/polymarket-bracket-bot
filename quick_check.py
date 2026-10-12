import asyncio
from polymarket_api import PolymarketAPI
from config import Config

async def f():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    print('Markets fetched:', len(markets))
    # Check config
    print('MIN_LIQUIDITY_USDC', Config.MIN_LIQUIDITY_USDC)
    print('MAX_MARKETS_PER_SCAN', Config.MAX_MARKETS_PER_SCAN)
    # Look for any market where best ask sum < 1
    found = []
    for m in markets[:100]:
        if len(m.clob_token_ids) != 2:
            continue
        yes_id, no_id = m.clob_token_ids
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yes_best = min(yes_book.asks, key=lambda a: float(a['price']))
        no_best = min(no_book.asks, key=lambda a: float(a['price']))
        total = float(yes_best['price']) + float(no_best['price'])
        if total < 1.0:
            found.append((total, m.question[:60]))
    print('Found brackets:', len(found))
    for t, q in found:
        print(t, q)

asyncio.run(f())
