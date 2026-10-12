import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    # Change sort to liquidity lowest first
    old_sort = Config.SCAN_SORT_BY
    # We'll manually fetch with different params
    from config import Config
    # Temporarily patch
    Config.SCAN_SORT_BY = 'liquidity'
    markets2 = await api.fetch_active_markets(limit=500)
    Config.SCAN_SORT_BY = old_sort
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets2]
    books = await api.fetch_order_books_batch(token_pairs, batch_size=20)
    found = 0
    for m, (yes_b, no_b) in zip(markets2, books):
        if not yes_b or not no_b: continue
        if not yes_b.asks or not no_b.asks: continue
        if m.liquidity < 100: continue
        yes_price = float(min(yes_b.asks, key=lambda a: float(a['price']))['price'])
        no_price = float(min(no_b.asks, key=lambda a: float(a['price']))['price'])
        total = yes_price + no_price
        if total < 1.0:
            found += 1
            print(f"BRACKET: {m.question[:80]} total {total:.4f}")
    print(f"Found {found}")

asyncio.run(test())
