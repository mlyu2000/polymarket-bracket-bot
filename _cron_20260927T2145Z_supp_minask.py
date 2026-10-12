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
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            y = min(float(a['price']) for a in yb.asks)
            n = min(float(a['price']) for a in nb.asks)
            rows.append((y + n, m.question[:60], y, n, m.liquidity))
    rows.sort()
    return rows, dt, len(markets)

rows, dt, nm = asyncio.run(scan())
brackets = [r for r in rows if r[0] < 1.0]
near = [r for r in rows if 1.0 <= r[0] <= 1.005]
print(f"[min-ask pass] {nm} markets in {dt:.1f}s; priced={len(rows)}")
print(f"[min-ask] true brackets (min-ask sum < 1.00): {len(brackets)}")
for s, q, y, n, liq in brackets[:10]:
    print(f"  {s:.3f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")
print(f"[min-ask] near-misses (<=1.005): {len(near)}")
for s, q, y, n, liq in near[:5]:
    print(f"  {s:.3f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")
