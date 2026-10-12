"""Supplementary near-miss scan using BEST asks (min price), not asks[0].
Polymarket CLOB /book lists asks DESC-sorted, so asks[0] is the worst price;
the verbatim cron script's near-miss block under-reports. This uses min()
consistent with detector.py logic."""
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
    scan_time = time.time() - t0

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
    return len(markets), priced, rows, scan_time

n, priced, rows, scan_time = asyncio.run(scan())
print(f"Best-ask floor scan: {n} markets, {priced} with both-side asks, {scan_time:.1f}s")
print("Lowest 10 Yes+No best-ask sums:")
for total, q, ya, na, liq in rows[:10]:
    print(f"  {total:.4f} | Yes@{ya:.4f} No@{na:.4f} | liq={liq} | {q}")
near = [r for r in rows if 1.0 <= r[0] <= 1.005]
below = [r for r in rows if r[0] < 1.0]
print(f"Near-misses (1.000-1.005, best-ask): {len(near)}")
print(f"Below-1.000 (best-ask): {len(below)}")
