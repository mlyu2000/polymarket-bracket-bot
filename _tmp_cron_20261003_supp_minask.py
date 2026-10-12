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
    rows = []
    brk = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            ya = min(float(a['price']) for a in yb.asks)
            na = min(float(a['price']) for a in nb.asks)
            s = ya + na
            if s < 1.0:
                brk.append((s, ya, na, m.question[:60], m.liquidity))
            rows.append((s, m.question[:55], ya, na, m.liquidity))
    rows.sort()
    brk.sort()
    return len(markets), brk, rows, time.time()-t0

n, brk, rows, dt = asyncio.run(scan())
print(f"min-ask floor scan: {n} markets in {dt:.1f}s")
print(f"TRUE BRACKETS (min-ask sum < 1.00): {len(brk)}")
for s, ya, na, q, liq in brk[:10]:
    print(f"  {s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
print("Top 10 lowest min-ask sums:")
for s, q, ya, na, liq in rows[:10]:
    print(f"  {s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
