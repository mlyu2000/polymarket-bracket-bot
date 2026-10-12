import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def check():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=100)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    results = []
    for m, (y,n) in zip(markets, books):
        if not y or not n or not y.asks or not n.asks:
            continue
        y_price = min(float(a['price']) for a in y.asks)
        n_price = min(float(a['price']) for a in n.asks)
        total = y_price + n_price
        results.append((total, m.question[:60], y_price, n_price, m.liquidity))
    results.sort(key=lambda x: x[0])
    for r in results[:20]:
        print(f"{r[0]:.4f} | Yes {r[2]:.3f} No {r[3]:.3f} | liq {r[4]:.0f} | {r[1]}")

asyncio.run(check())
