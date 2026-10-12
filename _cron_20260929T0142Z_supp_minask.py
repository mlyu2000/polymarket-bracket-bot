"""Supplemental near-miss/floor scan using BEST ask (min price) per book.

The verbatim cron script's near-miss block uses asks[0], which is the WORST
ask (CLOB /book returns asks DESC-sorted) and structurally reports ~0.
detector.py correctly uses min(); this supplement matches that method.
"""
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    near = []
    brackets_min = []
    sums = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        priced += 1
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        total = yp + np_
        sums.append((total, m.question[:50]))
        if total < 1.0:
            brackets_min.append((total, m.question[:60], yp, np_, m.liquidity))
        elif total <= 1.005:
            near.append((total, m.question[:50], yp, np_, m.liquidity))
    near.sort()
    brackets_min.sort()
    sums.sort()
    return len(markets), priced, scan_time, brackets_min, near, sums

async def main():
    nmarkets, priced, scan_time, brackets_min, near, sums = await scan()
    print(f"Markets: {nmarkets} | priced (both asks present): {priced} | fetch {scan_time:.1f}s")
    print(f"MIN-ASK brackets (sum<1.00): {len(brackets_min)}")
    for t, q, yp, np_, liq in brackets_min[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"MIN-ASK near-misses (1.00<sum<=1.005): {len(near)}")
    for t, q, yp, np_, liq in near[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print("FLOOR top-5 (lowest raw best-ask sums):")
    for s, q in sums[:5]:
        print(f"  {s:.4f} | {q}")

asyncio.run(main())
