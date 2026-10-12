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
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        tot = yp + np_
        priced += 1
        if tot <= 1.005:
            rows.append((tot, m.question[:55], yp, np_, m.liquidity))
    rows.sort()
    return len(markets), priced, rows, dt

markets, priced, rows, dt = asyncio.run(scan())
print(f"Supplement (min-ask): {markets} markets ({priced} priced) in {dt:.1f}s")
print(f"True brackets (min-ask sum < 1.00): {sum(1 for r in rows if r[0] < 1.0)}")
print(f"Near-misses (sum <= 1.005): {len(rows)}")
for tot, q, yp, np_, liq in rows[:8]:
    print(f"  {tot:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")
