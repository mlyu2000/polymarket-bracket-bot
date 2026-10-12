import asyncio, logging, time
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
            ya = min(float(a['price']) for a in yb.asks)
            na = min(float(a['price']) for a in nb.asks)
            rows.append((ya + na, m.question[:55], ya, na, m.liquidity))
    rows.sort()
    return rows

rows = asyncio.run(scan())
priced = [r for r in rows if r[0] > 0]
brackets = [r for r in priced if r[0] < 1.0]
near = [r for r in priced if 1.0 <= r[0] <= 1.005]
print(f"markets with both asks: {len(priced)}")
print(f"TRUE BRACKETS (min-ask sum < 1.00): {len(brackets)}")
for t, q, yp, np, liq in brackets[:10]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print(f"NEAR-MISS (1.000-1.005): {len(near)}")
for t, q, yp, np, liq in near[:10]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print("TOP-5 ABSOLUTE MIN SUMS (excl. zero-priced):")
for t, q, yp, np, liq in priced[:5]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
