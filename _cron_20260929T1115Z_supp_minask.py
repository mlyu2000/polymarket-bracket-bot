import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            rows.append((yp + np_, m.question[:60], yp, np_, m.liquidity))
    rows.sort()
    return rows

rows = asyncio.run(scan())
print(f"min-ask totals across {len(rows)} priced markets")
brackets = [r for r in rows if r[0] < 1.0]
nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
print(f"true brackets (min-ask sum < 1.00): {len(brackets)}")
for t, q, yp, np_, liq in brackets[:10]:
    print(f"  🔴 {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"true near-misses (1.000..1.005): {len(nm)}")
for t, q, yp, np_, liq in nm[:5]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
if rows:
    print(f"floor (lowest min-ask sum overall): {rows[0][0]:.4f} | {rows[0][1]}")
