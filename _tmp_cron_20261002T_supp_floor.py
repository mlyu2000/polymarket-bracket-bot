import asyncio, logging
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    sums = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            priced += 1
            t = min(float(a['price']) for a in yb.asks) + min(float(a['price']) for a in nb.asks)
            sums.append((t, m.question[:50], m.liquidity))
    sums.sort()
    print(f"priced markets: {priced}/{len(markets)}")
    if sums:
        print(f"min best-ask sum: {sums[0][0]:.4f}")
        n_below_1 = sum(1 for s in sums if s[0] < 1.000)
        n_le_1005 = sum(1 for s in sums if s[0] <= 1.005)
        print(f"best-ask sums <1.000: {n_below_1} | <=1.005: {n_le_1005}")
        for t, q, liq in sums[:10]:
            print(f"  [{t:.4f} | liq={liq} | {q}]")

asyncio.run(supp())
