"""Corrected near-miss pass: use min() best asks (API sends asks DESC)."""
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    priced = 0
    brackets = []
    near = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        if yp >= 1.0 or np_ >= 1.0 or yp <= 0 or np_ <= 0:
            continue
        priced += 1
        total = yp + np_
        if total < 1.0:
            ys = min(int(float(a['size'])) for a in yes_book.asks if float(a['price']) == yp)
            ns = min(int(float(a['size'])) for a in no_book.asks if float(a['price']) == np_)
            brackets.append((total, m.question[:60], yp, np_, m.liquidity, ys, ns))
        elif total <= 1.005:
            near.append((total, m.question[:50], yp, np_, m.liquidity))
    near.sort()
    brackets.sort()
    return markets, priced, brackets, near, scan_time

markets, priced, brackets, near, scan_time = asyncio.run(scan())
print(f"[min-ask pass] {len(markets)} markets, {priced} priced, in {scan_time:.1f}s")
print(f"TRUE BRACKETS (best-ask sum < 1.00): {len(brackets)}")
for total, q, yp, np_, liq, ys, ns in brackets[:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | sizes {ys}/{ns} | {q}")
print(f"Near-misses (<=1.005): {len(near)}")
for total, q, yp, np_, liq in near[:8]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
