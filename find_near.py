import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def find():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=200)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    results = []
    for m, (y, n) in zip(markets, books):
        if not y or not n or not y.asks or not n.asks:
            continue
        yes_price = min(float(a['price']) for a in y.asks)
        no_price = min(float(a['price']) for a in n.asks)
        total = yes_price + no_price
        if total <= 1.005:
            results.append((total, m.question[:60], yes_price, no_price, m.liquidity))
    results.sort()
    print(f"Found {len(results)} near")
    for r in results[:20]:
        print(r)

asyncio.run(find())
