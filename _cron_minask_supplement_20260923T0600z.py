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
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        if m.liquidity <= 0:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np = min(float(a['price']) for a in nb.asks)
        if yp <= 0 or np <= 0 or yp >= 1 or np >= 1:
            continue
        rows.append((yp + np, m.question[:55], yp, np, m.liquidity))
    rows.sort()
    return rows

rows = asyncio.run(scan())
print(f"priced markets (min-ask): {len(rows)}")
brackets = [r for r in rows if r[0] < 1.0]
near = [r for r in rows if 1.0 <= r[0] <= 1.005]
print(f"true brackets (sum<1.00): {len(brackets)}")
for s, q, yp, np, liq in brackets[:10]:
    print(f"  🔴 {s:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} | {q}")
print(f"near-misses (1.000-1.005): {len(near)}")
for s, q, yp, np, liq in near[:10]:
    print(f"  {s:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} | {q}")
if rows:
    print(f"floor (min sum): {rows[0][0]:.4f}")
