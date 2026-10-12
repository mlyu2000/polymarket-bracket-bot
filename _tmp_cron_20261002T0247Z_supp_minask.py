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
    dt = time.time() - t0

    rows = []
    skipped = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            skipped += 1
            continue
        yes_best = min(float(a['price']) for a in yes_book.asks)
        no_best = min(float(a['price']) for a in no_book.asks)
        rows.append((yes_best + no_best, m.question[:50], yes_best, no_best, m.liquidity))

    rows.sort()
    print(f"🔍 Best-ask recheck: {len(markets)} markets in {dt:.1f}s | books usable={len(rows)} skipped={skipped}")
    print(f"📊 TRUE near-misses (best-ask sum <= 1.005): {sum(1 for r in rows if r[0] <= 1.005)}")
    print(f"📊 sums < 1.01: {sum(1 for r in rows if r[0] < 1.01)}")
    print("Top 10 lowest best-ask sums:")
    for total, q, yp, np, liq in rows[:10]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    if rows:
        print(f"Absolute floor this run: {rows[0][0]:.3f}")

asyncio.run(scan())
