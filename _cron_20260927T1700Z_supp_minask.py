"""Supplement: correct near-miss floor using min(asks) per book
(CLOB /book asks are DESC-sorted; asks[0] is the WORST ask, per memory note)."""
import asyncio, json, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        rows.append((yp + np_, m.question[:50], yp, np_, m.liquidity))
    rows.sort()
    print(f"markets with both books: {len(rows)}")
    print("== TRUE min-ask floor (top 5, any total) ==")
    for t, q, yp, np_, liq in rows[:5]:
        print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")
    print("== TRUE near-misses <=1.005 ==")
    nm = [r for r in rows if r[0] <= 1.005]
    for t, q, yp, np_, liq in nm[:10]:
        print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")
    brackets = [r for r in rows if r[0] < 1.0]
    print(f"== TRUE brackets (min-ask sum < 1.00): {len(brackets)} ==")
    for t, q, yp, np_, liq in brackets:
        print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")
    with open('runs/scan_20260927T1700Z_floor.json', 'w') as f:
        json.dump({'ts': '2026-09-27T1700Z', 'priced': len(rows),
                   'floor': rows[0][0] if rows else None,
                   'near_misses_le_1.005': nm,
                   'brackets_lt_1.00': brackets}, f, indent=1)

asyncio.run(main())
