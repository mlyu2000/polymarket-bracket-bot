import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs, batch_size=20)
    found = []
    for m, (yes_b, no_b) in zip(markets, books):
        if not yes_b or not no_b: continue
        if not yes_b.asks or not no_b.asks: continue
        yes_price = float(min(yes_b.asks, key=lambda a: float(a['price']))['price'])
        no_price = float(min(no_b.asks, key=lambda a: float(a['price']))['price'])
        total = yes_price + no_price
        if total < 1.0:
            found.append((total, m.question[:80], m.liquidity))
    print(f"Found {len(found)} brackets with liquidity any")
    for f in found[:20]:
        print(f)

asyncio.run(test())
