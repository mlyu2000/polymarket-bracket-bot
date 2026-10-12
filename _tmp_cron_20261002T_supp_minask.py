# Supplementary: correct near-miss computation using BEST ask (min price).
# Known fact: CLOB /book returns asks DESC-sorted, so asks[0] is the WORST ask
# (~0.999). detector.py already uses min() correctly; only the cron near-miss
# block is affected. This script re-scans with min(asks) to get true totals.
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    if not book or not getattr(book, 'asks', None):
        return None
    return min(float(a['price']) for a in book.asks)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    detected, true_near, priced = [], [], 0
    floor = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        ya, na = best_ask(yes_book), best_ask(no_book)
        if ya is None or na is None:
            continue
        priced += 1
        total = ya + na
        if floor is None or total < floor[0]:
            floor = (total, m.question[:60], ya, na)
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            detected.append((opp.total_cost, opp.net_edge, opp.max_shares, m.question[:60], m.liquidity))
        elif total <= 1.005:
            true_near.append((total, m.question[:50], ya, na, m.liquidity))
    return len(markets), priced, detected, sorted(true_near), floor

markets, priced, detected, near, floor = asyncio.run(scan())
print(f"[supp] markets={markets} priced_books={priced}")
print(f"[supp] detector-brackets={len(detected)}")
for t, e, s, q, liq in sorted(detected):
    print(f"  🔴 sum={t:.3f} edge={e:.4f} shares={s} liq={liq} | {q}")
print(f"[supp] true near-misses (best-ask sum<=1.005): {len(near)}")
for total, q, yp, np, liq in near[:8]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
if floor:
    print(f"[supp] min best-ask sum = {floor[0]:.4f} | Yes@{floor[2]:.3f} No@{floor[3]:.3f} | {floor[1]}")
