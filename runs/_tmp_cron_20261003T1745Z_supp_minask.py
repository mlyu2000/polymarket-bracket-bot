"""Supplementary: true best-ask (min) near-misses + floor. asks[0] is WORST ask
(CLOB /book asks are DESC-sorted), so prompt-logic near-misses under-report."""
import asyncio
from polymarket_api import PolymarketAPI

async def main():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        if not (yb and nb and yb.asks and nb.asks):
            continue
        priced += 1
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        rows.append((yp + np_, m.question[:55], yp, np_, m.liquidity))
    rows.sort()
    if rows:
        print(f"best-ask floor: {rows[0][0]:.4f} ({rows[0][1]})")
    else:
        print("no priced markets")
    print(f"markets={len(markets)} priced={priced}")
    for thr in (1.000, 1.001, 1.005, 1.01):
        print(f"count sum<={thr:.3f}: {sum(1 for r in rows if r[0] <= thr)}")
    print("top-8 best-ask totals:")
    for total, q, yp, np_, liq in rows[:8]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(main())
