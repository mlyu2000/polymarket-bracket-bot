"""Supplementary near-miss/floor scan using BEST asks (min price), not asks[0].
Polymarket CLOB /book lists asks DESC-sorted, so asks[0] is the worst price (~0.999);
the verbatim cron script's near-miss block under-reports (known issue, see memory
2026-09-21). This mirrors detector.py's min() logic for an honest floor picture."""
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    elapsed = time.time() - t0

    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        priced += 1
        rows.append((ya + na, m.question[:55], ya, na, m.liquidity))
    rows.sort()
    return len(markets), priced, rows, elapsed

n, priced, rows, elapsed = asyncio.run(scan())
print(f"Best-ask floor scan: {n} markets, {priced} with both-side asks, {elapsed:.1f}s")
brackets = [r for r in rows if r[0] < 1.0]
near = [r for r in rows if 1.0 <= r[0] <= 1.005]
print(f"true brackets (min-ask sum < 1.00): {len(brackets)}")
for total, q, ya, na, liq in brackets[:10]:
    print(f"  🔴 {total:.4f} | Yes@{ya:.4f} No@{na:.4f} | liq={liq} | {q}")
print(f"true near-misses (1.000-1.005): {len(near)}")
for total, q, ya, na, liq in near[:10]:
    print(f"  {total:.4f} | Yes@{ya:.4f} No@{na:.4f} | liq={liq} | {q}")
print("Lowest 5 sums overall:")
for total, q, ya, na, liq in rows[:5]:
    print(f"  {total:.4f} | Yes@{ya:.4f} No@{na:.4f} | liq={liq} | {q}")