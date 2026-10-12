import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
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
            np_ = min(float(a['price']) for a in nb.asks)
            rows.append((yp + np_, m.question[:60], yp, np_, m.liquidity))
    rows.sort()
    return rows, len(markets), dt

rows, n, dt = asyncio.run(scan())
print(f"min-ask floor scan: {n} markets in {dt:.1f}s")
print("top 10 by sum(min asks):")
for s, q, yp, np_, liq in rows[:10]:
    print(f"  {s:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
under = [r for r in rows if r[0] <= 1.005]
print(f"count sum<=1.005: {len(under)}")
print(f"count sum<1.00: {len([r for r in rows if r[0] < 1.0])}")
