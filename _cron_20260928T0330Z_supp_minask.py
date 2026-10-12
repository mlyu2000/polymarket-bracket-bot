"""Supplement: TRUE near-miss floor using min(asks) per book
(CLOB /book asks are DESC-sorted; asks[0] is the WORST ask ~0.999, per memory note)."""
import asyncio, json, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0
    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        rows.append((round(yp + np_, 6), m.question[:50], yp, np_, m.liquidity))
    rows.sort()
    print(f"scan_time={dt:.1f}s markets={len(markets)} priced_both_books={len(rows)}")
    print("== TRUE min-ask floor (top 5, any total) ==")
    for t, q, yp, np_, liq in rows[:5]:
        print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")
    nm = [r for r in rows if r[0] <= 1.005]
    print(f"== TRUE near-misses <=1.005: {len(nm)} ==")
    for t, q, yp, np_, liq in nm[:10]:
        print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")
    brackets = [r for r in rows if r[0] < 1.0]
    print(f"== TRUE brackets (min-ask sum < 1.00): {len(brackets)} ==")
    for t, q, yp, np_, liq in brackets:
        print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")
    with open('runs/scan_20260928T0330Z_floor.json', 'w') as f:
        json.dump({'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                   'markets': len(markets), 'priced': len(rows),
                   'floor': rows[0][0] if rows else None,
                   'near_misses_le_1p005': nm,
                   'brackets_lt_1p00': brackets}, f, indent=1)

asyncio.run(main())
