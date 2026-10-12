import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=1000)
    print(f"Fetched {len(markets)}")
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    best_sums = []
    for m, (yb, nb) in zip(markets, books):
        if yb and nb and yb.asks and nb.asks:
            yes_min = min(float(a['price']) for a in yb.asks)
            no_min = min(float(a['price']) for a in nb.asks)
            total = yes_min + no_min
            if total < 1.01:
                best_sums.append((total, m.question[:70], m.liquidity))
    best_sums.sort(key=lambda x: x[0])
    print(f"Found {len(best_sums)} markets with sum <1.01")
    for s,q,l in best_sums[:20]:
        print(f"{s:.4f} | liq={l:.1f} | {q}")

asyncio.run(test())
