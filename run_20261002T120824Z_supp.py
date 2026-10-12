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

    near_misses = []
    floor_all = None
    n_opps = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            n_opps += 1
        if yes_book and no_book and yes_book.asks and no_book.asks:
            # CLOB /book asks are DESC-sorted; best ask = min price
            yes_best = min(float(a['price']) for a in yes_book.asks)
            no_best = min(float(a['price']) for a in no_book.asks)
            total = yes_best + no_best
            if floor_all is None or total < floor_all[0]:
                floor_all = (total, m.question[:60], yes_best, no_best, m.liquidity)
            if opp is None and total <= 1.005:
                near_misses.append((total, m.question[:50], yes_best, no_best, m.liquidity))

    near_misses.sort()
    return len(markets), n_opps, near_misses, floor_all, scan_time

n_markets, n_opps, near_misses, floor_all, scan_time = asyncio.run(scan())
print(f"MIN-ASK SCAN: {n_markets} markets in {scan_time:.1f}s (detector opps={n_opps})")
if floor_all:
    print(f"FLOOR (best yes+no ask): {floor_all[0]:.4f} | Yes@{floor_all[2]:.3f} No@{floor_all[3]:.3f} | liq={floor_all[4]} | {floor_all[1]}")
print(f"NEAR-MISS <=1.005 (min-ask): {len(near_misses)}")
for total, q, yp, np, liq in near_misses[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
