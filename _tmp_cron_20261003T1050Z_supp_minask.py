# Supplement: true min-ask near-misses (asks are DESC-sorted in CLOB /book; asks[0] is worst)
import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)

    rows = []
    brackets = []
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        ya = min(float(a['price']) for a in yb.asks)
        na = min(float(a['price']) for a in nb.asks)
        total = ya + na
        if total < 1.00:
            brackets.append((total, m.question[:60], ya, na, m.liquidity))
        elif total <= 1.005:
            rows.append((total, m.question[:60], ya, na, m.liquidity))
    rows.sort()
    brackets.sort()
    print(f"markets={len(markets)}")
    print(f"TRUE_MIN_ASK_BRACKETS(sum<1.00)={len(brackets)}")
    for t, q, ya, na, liq in brackets[:10]:
        print(f"  BRACKET {t:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    print(f"TRUE_NEAR_MISSES(<=1.005)={len(rows)}")
    for t, q, ya, na, liq in rows[:10]:
        print(f"  {t:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    all_totals = []
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        all_totals.append(min(float(a['price']) for a in yb.asks) + min(float(a['price']) for a in nb.asks))
    if all_totals:
        print(f"floor(min sum across all priced markets)={min(all_totals):.4f} priced={len(all_totals)}")

asyncio.run(main())
