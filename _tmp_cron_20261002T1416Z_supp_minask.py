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
    brackets = 0
    near = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            priced += 1
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            t = yp + np_
            sums.append((t, m.question[:50], m.liquidity, yp, np_))
            if t < 1.0:
                brackets += 1
            elif t <= 1.005:
                near.append((t, m.question[:50], m.liquidity, yp, np_))
    sums.sort()
    near.sort()
    print(f"priced markets: {priced}/{len(markets)}")
    print(f"true brackets on best asks (sum<1.00): {brackets}")
    if sums:
        print(f"min best-ask sum (floor): {sums[0][0]:.4f}")
    print(f"near-misses best-ask (<=1.005): {len(near)}")
    for t, q, liq, yp, np_ in near[:8]:
        print(f"  [{t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}]")
    print("top-8 lowest sums overall:")
    for t, q, liq, yp, np_ in sums[:8]:
        print(f"  [{t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}]")

asyncio.run(supp())
