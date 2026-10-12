"""Supplementary: best-ask (min) based totals — asks[0] is worst ask (~0.999,
CLOB returns asks DESC-sorted), so the verbatim near-miss block under-reports.
This recomputes near-misses using min price like detector.py does."""
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
    floor_sum = 2.0
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        if m.liquidity <= 0:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        if yp <= 0 or np_ <= 0 or yp >= 1 or np_ >= 1:
            continue
        total = yp + np_
        floor_sum = min(floor_sum, total)
        if total <= 1.005:
            rows.append((total, m.question[:55], yp, np_, m.liquidity))
    rows.sort()
    return rows, floor_sum, len(markets)

rows, floor_sum, nm = asyncio.run(scan())
print(f"MIN-ASK check over {nm} markets")
print(f"Best floor sum: {floor_sum:.4f}")
print(f"Near-misses (min-ask sum <= 1.005): {len(rows)}")
for total, q, yp, np_, liq in rows[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq=${liq:,.0f} | {q}")
