# Supplementary: correct min-ask near-miss analysis (asks[0] is the WORST ask,
# CLOB returns asks DESC-sorted; detector.py uses min() but the cron script's
# near-miss block uses asks[0] which inflates totals to ~0.999+~0.999).
import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)

    priced = 0
    rows = []
    floor = 2.0
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        if yp <= 0 or np_ <= 0 or yp >= 1 or np_ >= 1:
            continue
        priced += 1
        total = yp + np_
        if total < floor:
            floor = total
        if total <= 1.005 and m.liquidity > 0:
            rows.append((total, m.question[:50], yp, np_, m.liquidity))

    rows.sort()
    print(f"Priced markets: {priced}")
    print(f"Floor (min yes+no best-ask sum): {floor:.4f}")
    print(f"Near-misses <=1.005 (min-ask, liq>0): {len(rows)}")
    for t, q, y, n, l in rows[:10]:
        print(f"  {t:.4f} | Yes@{y:.3f} No@{n:.3f} | liq={l} | {q}")

asyncio.run(main())
