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
        if m.liquidity <= 0:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np = min(float(a['price']) for a in nb.asks)
        if yp >= 1.0 or np >= 1.0 or yp <= 0 or np <= 0:
            continue
        priced += 1
        rows.append((yp + np, m.question[:60], yp, np, m.liquidity))
    rows.sort()
    return len(markets), priced, rows

n, priced, rows = asyncio.run(scan())
print(f"Markets: {n} | priced: {priced}")
print("TRUE best-ask floor (top 8 by sum=min ask):")
for s, q, yp, np, liq in rows[:8]:
    print(f"  {s:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} | {q}")
br = [r for r in rows if r[0] < 1.0]
print(f"sum<1.00 (best-ask): {len(br)}")
for s, q, yp, np, liq in br:
    print(f"  🔴 {s:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} | {q}")
