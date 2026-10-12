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
            yp = min(float(a['price']) for a in yb.asks)
            np = min(float(a['price']) for a in nb.asks)
            rows.append((yp + np, m.question[:55], yp, np, m.liquidity))
    rows.sort()
    return len(markets), rows, dt

n, rows, dt = asyncio.run(scan())
brackets = [r for r in rows if r[0] < 1.00]
nm = [r for r in rows if 1.00 <= r[0] <= 1.005]
print(f"[min-ask recheck] {n} markets in {dt:.1f}s | priced={len(rows)}")
print(f"BRACKETS (sum<1.00): {len(brackets)}")
for s, q, yp, np, liq in brackets[:10]:
    print(f"  {s:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print(f"NEAR-MISS (<=1.005): {len(nm)}")
for s, q, yp, np, liq in nm[:10]:
    print(f"  {s:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print("FLOOR top5:")
for s, q, yp, np, liq in rows[:5]:
    print(f"  {s:.3f} | {q}")
