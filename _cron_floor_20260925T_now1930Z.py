import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        s = yp + np_
        priced += 1
        rows.append((s, m.question[:60], yp, np_, m.liquidity))
    rows.sort()
    return priced, rows

priced, rows = asyncio.run(scan())
print(f"Priced markets (best-ask floor): {priced}")
print(f"Absolute floor: {rows[0][0]:.4f}" if rows else "no data")
print(f"Brackets sum < 1.000 : {sum(1 for r in rows if r[0] < 1.0)}")
print(f"Near-misses <=1.005  : {sum(1 for r in rows if r[0] <= 1.005)}")
print("Top 8 lowest sums (best-ask):")
for s, q, yp, np_, liq in rows[:8]:
    print(f"  {s:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:,.0f} | {q}")
