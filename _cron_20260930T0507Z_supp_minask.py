# Supplementary: near-misses computed with BEST (min) ask instead of asks[0],
# matching detector.py logic (CLOB asks are DESC-sorted).
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
    near_misses = []
    true_min = (9.0, None)
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append((opp.total_cost, opp.net_edge, opp.yes_price, opp.no_price, opp.max_shares, m.question[:60]))
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                priced += 1
                yp = min(float(a['price']) for a in yes_book.asks)
                np = min(float(a['price']) for a in no_book.asks)
                total = yp + np
                if total < true_min[0]:
                    true_min = (total, m.question[:60])
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yp, np, m.liquidity))

    near_misses.sort()
    return markets, opps, near_misses, true_min, priced, scan_time

markets, opps, near_misses, true_min, priced, scan_time = asyncio.run(scan())
print(f"markets={len(markets)} priced_books={priced} scan_time={scan_time:.1f}s")
print(f"BRACKETS(min-ask): {len(opps)}")
for s, e, y, n, sh, q in sorted(opps):
    print(f"  sum={s:.4f} edge={e:.4f} Yes@{y:.3f} No@{n:.3f} shares={sh} | {q}")
print(f"Near-misses <=1.005 (min-ask): {len(near_misses)}")
for total, q, yp, np, liq in near_misses[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print(f"True global min sum: {true_min[0]:.4f} | {true_min[1]}")
