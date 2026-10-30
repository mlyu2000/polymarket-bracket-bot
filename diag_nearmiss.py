"""Diagnostic: corrected near-miss scan using min(all asks) — the asks[0]
worst-ask approach is a known artifact that reports 0 near-misses."""
import asyncio, logging, time
from collections import Counter
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

    two_sided = 0
    near_misses = []  # sum using min-ask
    buckets = Counter()
    min_ask_total = []  # all min-ask sums for distribution

    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book:
            continue
        if not yes_book.asks or not no_book.asks:
            continue
        yes_ask = min(yes_book.asks, key=lambda a: float(a["price"]))
        no_ask = min(no_book.asks, key=lambda a: float(a["price"]))
        yp = float(yes_ask["price"])
        np = float(no_ask["price"])
        if yp <= 0 or np <= 0 or yp >= 1.0 or np >= 1.0:
            continue
        two_sided += 1
        total = yp + np
        min_ask_total.append(total)
        buckets[f"{total:.3f}"] += 1
        if total <= 1.005:
            near_misses.append((total, m.question[:50], yp, np, m.liquidity))

    # Also report asks[0] artifact for comparison
    asks0_near = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book:
            continue
        if not yes_book.asks or not no_book.asks:
            continue
        yp0 = float(yes_book.asks[0]["price"])
        np0 = float(no_book.asks[0]["price"])
        if yp0 <= 0 or np0 <= 0 or yp0 >= 1.0 or np0 >= 1.0:
            continue
        if yp0 + np0 <= 1.005:
            asks0_near += 1

    near_misses.sort()
    min_ask_total.sort()
    median = min_ask_total[len(min_ask_total)//2] if min_ask_total else 0

    print(f"🔍 Markets fetched: {len(markets)} | scan time: {scan_time:.1f}s")
    print(f"📊 Two-sided books (both have asks): {two_sided}")
    print(f"✅ Min-ask near-misses (sum <= 1.005): {len(near_misses)}")
    for total, q, yp, np, liq in near_misses[:10]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} | {q}")
    print(f"\n📈 Min-ask sum distribution: median={median:.3f}, min={min_ask_total[0]:.3f}" if min_ask_total else "")
    print(f"   tiers: le1.005={sum(1 for t in min_ask_total if t<=1.005)}, "
          f"le1.010={sum(1 for t in min_ask_total if t<=1.010)}, "
          f"le1.020={sum(1 for t in min_ask_total if t<=1.020)}, "
          f"le1.050={sum(1 for t in min_ask_total if t<=1.050)}, "
          f"lt1.000={sum(1 for t in min_ask_total if t<1.000)}")
    print(f"\n🐛 asks[0] artifact near-misses: {asks0_near} (uses worst ask — NOT valid)")

result = asyncio.run(scan())
