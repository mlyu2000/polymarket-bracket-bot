import asyncio
from polymarket_api import PolymarketAPI

async def test():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=100)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    samples = []
    for m, (yb, nb) in zip(markets, books):
        if yb and nb and yb.asks and nb.asks:
            yes0 = float(yb.asks[0]['price'])
            no0 = float(nb.asks[0]['price'])
            total0 = yes0 + no0
            yes_min = min(float(a['price']) for a in yb.asks)
            no_min = min(float(a['price']) for a in nb.asks)
            total_min = yes_min + no_min
            if total_min < 1.01:
                samples.append((total0, total_min, m.question[:60]))
    samples.sort(key=lambda x: x[1])
    for t0, tmin, q in samples[:20]:
        print(f"asks0_sum={t0:.3f} min_sum={tmin:.3f} | {q}")

asyncio.run(test())
