"""Supplementary scan: use min(all asks) instead of asks[0] to avoid the
CLOB descending-order artifact. Cross-checks the main scan output."""

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

    real_min_brackets = []   # real brackets: min yes + min no < 1.00
    real_near_misses = []    # min sum <= 1.005

    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        if not m.active or m.closed or m.liquidity <= 0:
            continue
        # Use min of all asks — the correct best-ask
        yes_min = min(float(a['price']) for a in yes_book.asks)
        no_min = min(float(a['price']) for a in no_book.asks)
        total = yes_min + no_min
        if total < 1.00:
            real_min_brackets.append((total, yes_min, no_min, m.question[:60], m.liquidity))
        elif total <= 1.005:
            real_near_misses.append((total, yes_min, no_min, m.question[:50], m.liquidity))

    real_min_brackets.sort()
    real_near_misses.sort()

    print(f"🔍 Supp scan: {len(markets)} markets in {scan_time:.1f}s")
    print(f"✅ REAL BRACKETS (min-ask sum < 1.00): {len(real_min_brackets)}")
    for total, yp, np, q, liq in real_min_brackets[:10]:
        print(f"  🔴 {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq=${liq:,.0f} | {q}")
    print(f"📊 Near-misses (min-ask sum ≤1.005): {len(real_near_misses)}")
    for total, yp, np, q, liq in real_near_misses[:5]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")

asyncio.run(scan())
