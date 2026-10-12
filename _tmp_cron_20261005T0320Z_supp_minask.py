# Supplement: near-misses recomputed with BEST asks (min price). CLOB /book returns
# asks DESC-sorted, so asks[0] is the WORST ask (~0.999) and the prompt near-miss
# block systematically overstates totals. detector.py itself uses min() correctly.
import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan_best():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    priced = 0
    brackets = []
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        priced += 1
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        total = yp + np_
        rows.append((total, m.question[:60], yp, np_, m.liquidity))
        if total < 1.00:
            brackets.append((total, m.question[:60], yp, np_, m.liquidity))
    rows.sort()
    return priced, rows, brackets

priced, rows, brackets = asyncio.run(scan_best())
print(f"priced markets (best-ask): {priced}")
print(f"true brackets sum<1.00 on best asks: {len(brackets)}")
for total, q, yp, np_, liq in brackets[:10]:
    print(f"  🟢 {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print("top 10 closest (best asks):")
for total, q, yp, np_, liq in rows[:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
near = [r for r in rows if r[0] <= 1.005]
print(f"near-misses (≤1.005) on best asks: {len(near)}")
