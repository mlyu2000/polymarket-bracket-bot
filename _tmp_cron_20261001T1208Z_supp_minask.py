# Supplementary check: near-misses using BEST (min) asks, not asks[0].
# Known: CLOB /book returns asks DESC-sorted, so asks[0] is the worst price (~0.999).
# detector.py already uses min() correctly; this script corrects the near-miss block.
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    opps = []
    near = []
    true_min = None
    true_min_q = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append((opp.total_cost, opp.net_edge, opp.max_shares, m.question[:60], m.liquidity))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            total = ya + na
            if true_min is None or total < true_min:
                true_min, true_min_q = total, (m.question[:60], ya, na)
            if total <= 1.005:
                near.append((total, m.question[:50], ya, na, m.liquidity))

    near.sort()
    return len(markets), scan_time, opps, near, true_min, true_min_q

nm, st, opps, near, tmin, tminq = asyncio.run(scan())
print(f"[min-ask] {nm} markets in {st:.1f}s")
print(f"[min-ask] TRUE brackets (sum<1.00): {len(opps)}")
for s, e, sh, q, liq in sorted(opps):
    print(f"  {s:.4f} edge={e:.4f} shares={sh} liq={liq} | {q}")
print(f"[min-ask] near-misses (<=1.005): {len(near)}")
for total, q, ya, na, liq in near[:10]:
    print(f"  {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
print(f"[min-ask] global min sum: {tmin:.4f} | {tminq}")
