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
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append((opp.total_cost, opp.net_edge, opp.yes_price, opp.no_price, opp.max_shares, m.liquidity, m.question[:60]))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            total = yes_price + no_price
            if total <= 1.005:
                near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))
    near_misses.sort()
    return len(markets), priced, opps, near_misses, scan_time

markets_n, priced, opps, near_misses, scan_time = asyncio.run(scan())
print(f"[min-ask supplement] {markets_n} markets ({priced} priced) in {scan_time:.1f}s")
print(f"BRACKETS (detector, net_edge>=margin): {len(opps)}")
for t, e, yp, np_, sh, liq, q in sorted(opps):
    print(f"  sum={t:.3f} edge={e:.4f} Yes@{yp:.3f} No@{np_:.3f} shares={sh} liq={liq} | {q}")
print(f"Near-misses (best-ask sum <= 1.005): {len(near_misses)}")
for total, q, yp, np_, liq in near_misses[:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
if near_misses:
    print(f"FLOOR: {min(t for t,*_ in near_misses):.3f}")
