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
            np_ = min(float(a['price']) for a in nb.asks)
            rows.append((yp + np_, m.question[:60], yp, np_, m.liquidity))
    rows.sort()
    return rows, dt, len(markets)

rows, dt, n = asyncio.run(scan())
print(f"min-ask check: {n} markets in {dt:.1f}s")
print(f"true floor sum = {rows[0][0]:.4f}")
print(f"count sum<=1.00: {sum(1 for r in rows if r[0] < 1.0)}")
print(f"count sum<=1.005: {sum(1 for r in rows if r[0] <= 1.005)}")
for total, q, yp, np_, liq in rows[:8]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
