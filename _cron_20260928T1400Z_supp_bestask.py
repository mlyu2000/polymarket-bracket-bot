import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not (yb and nb and yb.asks and nb.asks):
            continue
        ya = min(float(a['price']) for a in yb.asks)
        na = min(float(a['price']) for a in nb.asks)
        s = ya + na
        priced += 1
        rows.append((s, m.question[:60], ya, na, m.liquidity))
    rows.sort()
    print(f"Supp best-ask scan: {len(markets)} markets, {priced} with both asks, in {dt:.1f}s")
    below1 = [r for r in rows if r[0] < 1.0]
    print(f"TRUE best-ask sums < 1.00: {len(below1)}")
    for s, q, ya, na, l in below1[:10]:
        print(f"  {s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={l} | {q}")
    print(f"Best-ask near-misses (1.000 < sum <= 1.005): {sum(1 for r in rows if 1.0 < r[0] <= 1.005)}")
    print("Top 10 lowest sums overall:")
    for s, q, ya, na, l in rows[:10]:
        print(f"  {s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={l} | {q}")

asyncio.run(scan())
