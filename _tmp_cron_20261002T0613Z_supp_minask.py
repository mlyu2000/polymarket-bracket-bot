"""Supplementary near-miss scan using BEST asks (min price), not asks[0].
Polymarket CLOB /book lists asks DESC-sorted, so asks[0] is the worst ask
(~0.999) and the verbatim near-miss block under-reports."""
import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if not (yb and nb and yb.asks and nb.asks):
            continue
        if m.liquidity <= 0:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        s = yp + np_
        rows.append((s, m.question[:60], yp, np_, m.liquidity))

    rows.sort()
    print(f"BEST-ASK totals scanned: {len(rows)}")
    below1 = [r for r in rows if r[0] < 1.0]
    print(f"sum < 1.000 (best asks): {len(below1)}")
    for r in below1[:10]:
        print(f"  🔴 {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]:.0f} | {r[1]}")
    print("Top near-misses (best asks, <=1.005):")
    n = [r for r in rows if 1.0 <= r[0] <= 1.005]
    for r in n[:10]:
        print(f"  {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]:.0f} | {r[1]}")
    if rows:
        print(f"Floor (min sum): {rows[0][0]:.4f}")

asyncio.run(main())
